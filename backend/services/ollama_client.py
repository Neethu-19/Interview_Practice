"""
Ollama Client for LLM Integration
Provides HTTP client for interacting with local Ollama server.
"""
import requests
import json
import time
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ValidationError


class OllamaClientError(Exception):
    """Base exception for Ollama client errors"""
    pass


class OllamaConnectionError(OllamaClientError):
    """Raised when connection to Ollama server fails"""
    pass


class OllamaGenerationError(OllamaClientError):
    """Raised when text generation fails"""
    pass


class OllamaClient:
    """
    HTTP client for Ollama API.
    
    Provides methods for text generation, structured output generation,
    and health checking with automatic retry logic.
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.1:8b",
        timeout: int = 60,
        max_retries: int = 3,
        initial_retry_delay: float = 1.0
    ):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Base URL for Ollama API (default: http://localhost:11434)
            model: Model name to use (default: llama3.1:8b)
            timeout: Request timeout in seconds (default: 60)
            max_retries: Maximum number of retry attempts (default: 3)
            initial_retry_delay: Initial delay between retries in seconds (default: 1.0)
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.initial_retry_delay = initial_retry_delay
        # Ollama API endpoints
        self.generate_endpoint = f"{self.base_url}/api/generate"
        self.chat_endpoint = f"{self.base_url}/api/chat"
        self.tags_endpoint = f"{self.base_url}/api/tags"
    
    def _exponential_backoff(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay.
        
        Args:
            attempt: Current attempt number (0-indexed)
            
        Returns:
            Delay in seconds
        """
        return self.initial_retry_delay * (2 ** attempt)
    
    def _make_request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> requests.Response:
        """
        Make HTTP request with exponential backoff retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response object
            
        Raises:
            OllamaConnectionError: If all retry attempts fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    **kwargs
                )
                response.raise_for_status()
                return response
                
            except requests.exceptions.ConnectionError as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = self._exponential_backoff(attempt)
                    time.sleep(delay)
                    continue
                    
            except requests.exceptions.Timeout as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = self._exponential_backoff(attempt)
                    time.sleep(delay)
                    continue
                    
            except requests.exceptions.HTTPError as e:
                # Don't retry on HTTP errors (4xx, 5xx)
                raise OllamaGenerationError(f"HTTP error: {e}") from e
                
            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = self._exponential_backoff(attempt)
                    time.sleep(delay)
                    continue
        
        # All retries exhausted
        raise OllamaConnectionError(
            f"Failed to connect to Ollama after {self.max_retries} attempts: {last_exception}"
        ) from last_exception
    
    def check_health(self) -> bool:
        """
        Check if Ollama server is available and responsive.
        
        Returns:
            True if server is healthy, False otherwise
        """
        try:
            response = self._make_request_with_retry(
                method="GET",
                url=self.tags_endpoint
            )
            return response.status_code == 200
            
        except (OllamaConnectionError, OllamaGenerationError):
            return False
    
    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """
        Generate text completion using Ollama.
        
        Args:
            prompt: User prompt for generation
            system: Optional system prompt to set context
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate (None for model default)
            stream: Whether to stream response (not implemented)
            
        Returns:
            Generated text as string
            
        Raises:
            OllamaConnectionError: If connection fails after retries
            OllamaGenerationError: If generation fails
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,  # We'll handle streaming in future if needed
            "options": {
                "temperature": temperature
            }
        }
        
        if system:
            payload["system"] = system
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        try:
            response = self._make_request_with_retry(
                method="POST",
                url=self.generate_endpoint,
                json=payload
            )
            
            result = response.json()
            
            if "response" not in result:
                raise OllamaGenerationError(
                    f"Unexpected response format: {result}"
                )
            
            return result["response"].strip()
            
        except json.JSONDecodeError as e:
            raise OllamaGenerationError(
                f"Failed to parse Ollama response: {e}"
            ) from e
    
    def generate_structured(
        self,
        prompt: str,
        system: Optional[str] = None,
        response_format: Optional[type[BaseModel]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate structured JSON output using Ollama.
        
        This method generates text and attempts to parse it as JSON.
        Optionally validates against a Pydantic model schema.
        
        Args:
            prompt: User prompt for generation
            system: Optional system prompt to set context
            response_format: Optional Pydantic model class for validation
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Parsed JSON as dictionary
            
        Raises:
            OllamaConnectionError: If connection fails after retries
            OllamaGenerationError: If generation or parsing fails
        """
        # Enhance prompt to request JSON output
        json_instruction = "\n\nRespond with valid JSON only. Do not include any explanatory text before or after the JSON."
        enhanced_prompt = prompt + json_instruction
        
        # Enhance system prompt if provided
        if system:
            enhanced_system = system + "\n\nYou must respond with valid JSON format only."
        else:
            enhanced_system = "You are a helpful assistant that responds with valid JSON format only."
        
        # Generate text
        response_text = self.generate(
            prompt=enhanced_prompt,
            system=enhanced_system,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Try to extract JSON from response
        # Sometimes LLMs wrap JSON in markdown code blocks
        cleaned_response = response_text.strip()
        
        # Remove markdown code blocks if present
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        elif cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        
        cleaned_response = cleaned_response.strip()
        
        # Parse JSON
        try:
            parsed_json = json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            raise OllamaGenerationError(
                f"Failed to parse JSON from response: {e}\nResponse: {response_text}"
            ) from e
        
        # Validate against Pydantic model if provided
        if response_format:
            try:
                validated = response_format(**parsed_json)
                return validated.model_dump()
            except ValidationError as e:
                raise OllamaGenerationError(
                    f"Response does not match expected format: {e}"
                ) from e
        
        return parsed_json
    
    def list_models(self) -> List[str]:
        """
        List available models on the Ollama server.
        
        Returns:
            List of model names
            
        Raises:
            OllamaConnectionError: If connection fails
        """
        try:
            response = self._make_request_with_retry(
                method="GET",
                url=self.tags_endpoint
            )
            
            result = response.json()
            
            if "models" not in result:
                return []
            
            return [model.get("name", "") for model in result["models"]]
            
        except json.JSONDecodeError as e:
            raise OllamaGenerationError(
                f"Failed to parse models list: {e}"
            ) from e
    
    def __repr__(self) -> str:
        return f"OllamaClient(base_url='{self.base_url}', model='{self.model}')"
