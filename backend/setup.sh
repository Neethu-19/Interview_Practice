#!/bin/bash
echo "Setting up Interview Practice Partner Backend..."
echo

echo "Creating virtual environment..."
python3 -m venv venv

echo
echo "Activating virtual environment..."
source venv/bin/activate

echo
echo "Installing dependencies..."
pip install -r requirements.txt

echo
echo "Setup complete!"
echo
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo
echo "To start the server, run:"
echo "  python main.py"
