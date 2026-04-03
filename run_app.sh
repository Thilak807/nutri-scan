#!/bin/bash

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Function to check if a Python package is installed
is_installed() {
    python -c "import $1" &> /dev/null
}

# Install Python dependencies if they are not already installed
if ! is_installed opencv-python; then
    pip install opencv-python
fi
if ! is_installed pytesseract; then
    pip install pytesseract
fi
if ! is_installed Flask; then
    pip install Flask
fi
if ! is_installed numpy; then
    pip install numpy
fi

# Run Flask server in one terminal
gnome-terminal -- bash -c "cd $SCRIPT_DIR/OCR; python3 flask_logic.py; exec bash"

# Run Flutter app in another terminal
gnome-terminal -- bash -c "cd $SCRIPT_DIR/ingr_detector; flutter run; exec bash"

