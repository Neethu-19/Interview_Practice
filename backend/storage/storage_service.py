"""
Storage service for persisting interview sessions, messages, and feedback.
"""

import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from storage.database import Database
from models.data_models import (
    Session, Message, FeedbackReport, SessionSummary, InterviewHistory
)


class StorageService:
    """Service for persisting and retrieving interview data."""
    
    def __init__(self, db_path: str = "interview_practice.db"):
        """
        Initialize storage service.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db = Database(db_path)
    
    def save_session(self, session: Session) -> bool:
        """
        Persist a new interview session.
        
        Args:
            session: Session object to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sessions 
                    (session_id, role, mode, created_at, status, 
                     current_question_index, followup_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(session.session_id),
                    session.role,
                    session.mode,
                    session.created_at.isoformat(),
                    session.status,
                    session.current_question_index,
                    session.followup_count
                ))
                return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def update_session(self, session: Session) -> bool:
        """
        Update an existing session.
        
        Args:
            session: Session object with updated data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE sessions 
                    SET status = ?,
                        current_question_index = ?,
                        followup_count = ?
                    WHERE session_id = ?
                """, (
                    session.status,
                    session.current_question_index,
                    session.followup_count,
                    str(session.session_id)
                ))
                return True
        except Exception as e:
            print(f"Error updating session: {e}")
            return False
    
    def save_message(self, session_id: UUID, message: Message) -> bool:
        """
        Store a conversation message.
        
        Args:
            session_id: ID of the session
            message: Message object to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO messages (session_id, type, content, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (
                    str(session_id),
                    message.type,
                    message.content,
                    message.timestamp.isoformat()
                ))
                return True
        except Exception as e:
            print(f"Error saving message: {e}")
            return False
    
    def save_feedback(self, feedback: FeedbackReport) -> bool:
        """
        Store performance feedback report.
        
        Args:
            feedback: FeedbackReport object to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO feedback 
                    (session_id, communication_score, technical_score, 
                     structure_score, strengths, improvements, overall_feedback)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(feedback.session_id),
                    feedback.scores.communication,
                    feedback.scores.technical_knowledge,
                    feedback.scores.structure,
                    json.dumps(feedback.strengths),
                    json.dumps(feedback.improvements),
                    feedback.overall_feedback
                ))
                return True
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return False

    def get_session(self, session_id: UUID) -> Optional[Session]:
        """
        Retrieve a session by ID.
        
        Args:
            session_id: UUID of the session
            
        Returns:
            Session object if found, None otherwise
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT session_id, role, mode, created_at,
                           status, current_question_index, followup_count
                    FROM sessions
                    WHERE session_id = ?
                """, (str(session_id),))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                # Fetch messages for this session
                messages = self._get_session_messages(session_id, conn)
                
                return Session(
                    session_id=UUID(row['session_id']),
                    role=row['role'],
                    mode=row['mode'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    status=row['status'],
                    current_question_index=row['current_question_index'],
                    followup_count=row['followup_count'],
                    messages=messages
                )
        except Exception as e:
            print(f"Error retrieving session: {e}")
            return None
    
    def _get_session_messages(self, session_id: UUID, conn) -> List[Message]:
        """
        Helper method to retrieve messages for a session.
        
        Args:
            session_id: UUID of the session
            conn: Database connection
            
        Returns:
            List of Message objects
        """
        cursor = conn.cursor()
        cursor.execute("""
            SELECT type, content, timestamp
            FROM messages
            WHERE session_id = ?
            ORDER BY timestamp ASC
        """, (str(session_id),))
        
        messages = []
        for row in cursor.fetchall():
            messages.append(Message(
                type=row['type'],
                content=row['content'],
                timestamp=datetime.fromisoformat(row['timestamp'])
            ))
        
        return messages
    
    def get_user_history(self, limit: Optional[int] = None) -> InterviewHistory:
        """
        Fetch all user sessions with summary information.
        
        Args:
            limit: Optional limit on number of sessions to return
            
        Returns:
            InterviewHistory object with session summaries
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT s.session_id, s.role, s.created_at, s.status,
                           COALESCE(
                               (f.communication_score + f.technical_score + f.structure_score) / 3.0,
                               0
                           ) as avg_score
                    FROM sessions s
                    LEFT JOIN feedback f ON s.session_id = f.session_id
                    ORDER BY s.created_at DESC
                """
                
                if limit:
                    query += f" LIMIT {limit}"
                
                cursor.execute(query)
                
                sessions = []
                total_score = 0
                count_with_scores = 0
                
                for row in cursor.fetchall():
                    score = float(row['avg_score'])
                    sessions.append(SessionSummary(
                        session_id=UUID(row['session_id']),
                        role=row['role'],
                        date=datetime.fromisoformat(row['created_at']),
                        score=score,
                        status=row['status']
                    ))
                    
                    if score > 0:
                        total_score += score
                        count_with_scores += 1
                
                avg_score = total_score / count_with_scores if count_with_scores > 0 else 0.0
                
                return InterviewHistory(
                    sessions=sessions,
                    total_interviews=len(sessions),
                    average_score=avg_score
                )
        except Exception as e:
            print(f"Error retrieving user history: {e}")
            return InterviewHistory(sessions=[], total_interviews=0, average_score=0.0)
    
    def get_session_transcript(self, session_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieve full conversation transcript with feedback.
        
        Args:
            session_id: UUID of the session
            
        Returns:
            Dictionary containing session info, messages, and feedback
        """
        try:
            with self.db.get_connection() as conn:
                # Get session info
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT session_id, role, mode, created_at, status
                    FROM sessions
                    WHERE session_id = ?
                """, (str(session_id),))
                
                session_row = cursor.fetchone()
                if not session_row:
                    return None
                
                # Get messages
                messages = self._get_session_messages(session_id, conn)
                
                # Get feedback if available
                cursor.execute("""
                    SELECT communication_score, technical_score, structure_score,
                           strengths, improvements, overall_feedback, created_at
                    FROM feedback
                    WHERE session_id = ?
                """, (str(session_id),))
                
                feedback_row = cursor.fetchone()
                feedback_dict = None
                
                if feedback_row:
                    feedback_dict = {
                        "scores": {
                            "communication": feedback_row['communication_score'],
                            "technical_knowledge": feedback_row['technical_score'],
                            "structure": feedback_row['structure_score']
                        },
                        "strengths": json.loads(feedback_row['strengths']),
                        "improvements": json.loads(feedback_row['improvements']),
                        "overall_feedback": feedback_row['overall_feedback'],
                        "generated_at": feedback_row['created_at']
                    }
                
                return {
                    "session_id": session_row['session_id'],
                    "role": session_row['role'],
                    "mode": session_row['mode'],
                    "created_at": session_row['created_at'],
                    "status": session_row['status'],
                    "transcript": [
                        {
                            "type": msg.type,
                            "content": msg.content,
                            "timestamp": msg.timestamp.isoformat()
                        }
                        for msg in messages
                    ],
                    "feedback": feedback_dict
                }
        except Exception as e:
            print(f"Error retrieving session transcript: {e}")
            return None
