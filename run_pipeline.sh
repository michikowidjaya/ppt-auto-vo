#!/bin/bash
# Simple wrapper script to run the PPTX to Video pipeline

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

# Check if required packages are installed
echo "Checking Python dependencies..."
python3 -c "import pptx, gtts, PIL" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "ERROR: FFmpeg is not installed"
    echo "Please install FFmpeg:"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    exit 1
fi

# Run the pipeline
echo "Starting PPTX to Video pipeline..."
python3 pptx_to_video.py "$@"
