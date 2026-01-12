# Quick Start Guide - Python PPTX to Video

## Installation (One-time setup)

### 1. Install System Dependencies

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip ffmpeg poppler-utils libreoffice
```

#### macOS:
```bash
brew install python3 ffmpeg poppler libreoffice
```

#### Windows:
1. Install Python 3 from [python.org](https://www.python.org/downloads/)
2. Install FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
3. (Optional) Install LibreOffice from [libreoffice.org](https://www.libreoffice.org/download/)

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Basic Usage

### Step 1: Prepare Your Presentation

Place your PowerPoint file in the `input/` directory:
```bash
cp your-presentation.pptx input/slides.pptx
```

Or use a custom name and specify it with `--pptx` flag.

### Step 2: Run the Pipeline

**Option A: Using the helper script (recommended)**
```bash
./run_pipeline.sh
```

**Option B: Direct Python command**
```bash
python3 pptx_to_video.py
```

### Step 3: Get Your Video

The final video will be in `output/output.mp4`

## Advanced Usage Examples

### Example 1: Indonesian Language
```bash
python3 pptx_to_video.py --language id
```

### Example 2: Custom File Name
```bash
# Place your file in input/my-slides.pptx
python3 pptx_to_video.py --pptx my-slides.pptx
```

### Example 3: Custom Directories
```bash
python3 pptx_to_video.py \
  --input ./presentations \
  --output ./videos \
  --temp ./tmp
```

### Example 4: Clean Start (Remove Old Cache)
```bash
python3 pptx_to_video.py --clean
```

### Example 5: All Options Combined
```bash
python3 pptx_to_video.py \
  --input ./my-presentations \
  --pptx company-overview.pptx \
  --output ./final-videos \
  --temp ./processing \
  --language id \
  --clean
```

## Common Scenarios

### Scenario 1: First Time User
```bash
# 1. Check if FFmpeg is installed
ffmpeg -version

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Put your PPTX in input folder
cp my-presentation.pptx input/slides.pptx

# 4. Run the pipeline
./run_pipeline.sh

# 5. Check the output
ls -lh output/output.mp4
```

### Scenario 2: Multiple Presentations
```bash
# Process first presentation
python3 pptx_to_video.py --pptx presentation1.pptx --clean
mv output/output.mp4 output/video1.mp4

# Process second presentation
python3 pptx_to_video.py --pptx presentation2.pptx --clean
mv output/output.mp4 output/video2.mp4
```

### Scenario 3: Batch Processing with Script
```bash
#!/bin/bash
# Save as: batch_convert.sh

for pptx in input/*.pptx; do
    filename=$(basename "$pptx")
    echo "Processing $filename..."
    python3 pptx_to_video.py --pptx "$filename" --clean
    mv output/output.mp4 "output/${filename%.pptx}.mp4"
done
```

## Troubleshooting

### Issue: "Module not found" Error
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

### Issue: "FFmpeg not found" Error
```bash
# Check if FFmpeg is installed
which ffmpeg

# If not installed:
# Ubuntu/Debian: sudo apt install ffmpeg
# macOS: brew install ffmpeg
```

### Issue: Poor Quality Slides
```bash
# Solution: Install LibreOffice for better rendering
# Ubuntu/Debian: sudo apt install libreoffice
# macOS: brew install --cask libreoffice
```

### Issue: No Audio Generated
This is normal if you don't have internet connection. The script will automatically create silent audio as fallback. The video will still be created successfully.

### Issue: Video Too Short/Long
The video duration depends on the audio length. To control duration:
1. Add more text to slides (longer audio = longer video)
2. Or modify the `create_silent_audio()` duration parameter in the script

## Understanding the Output

After successful execution, you'll see:
```
output/
└── output.mp4          # Final video (all slides combined)

temp/
├── slides/
│   ├── slide001.png    # PNG image of slide 1
│   ├── slide002.png    # PNG image of slide 2
│   └── ...
├── audio/
│   ├── slide001.mp3    # Audio for slide 1
│   ├── slide002.mp3    # Audio for slide 2
│   └── ...
└── videos/
    ├── slide001.mp4    # Video of slide 1 (image + audio)
    ├── slide002.mp4    # Video of slide 2 (image + audio)
    └── ...
```

The `temp/` directory contains all intermediate files and can be safely deleted after you have your final video.

## Tips for Best Results

1. **Use Clear Text**: The TTS works best with clear, properly punctuated text
2. **Optimize Slide Count**: More slides = longer processing time
3. **Check Output**: Always preview the final video before sharing
4. **Keep It Simple**: Avoid complex animations in PPTX (they won't be rendered)
5. **Use LibreOffice**: Install it for much better slide rendering quality

## Support

For more detailed information, see [README_PYTHON.md](README_PYTHON.md)
