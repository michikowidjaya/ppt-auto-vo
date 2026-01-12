# Quick Start Guide

## Python Implementation (Recommended for Beginners)

### Basic Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run with default settings
python3 pptx_to_video.py

# Run with custom background
python3 pptx_to_video.py --background input/background.png

# Run with Indonesian language
python3 pptx_to_video.py --language id

# Clean and run
python3 pptx_to_video.py --clean
```

### Using Custom Background

A default blue gradient background is included at `input/background.png`. To use your own:

1. Create or find a 1920x1080 PNG image
2. Place it in the `input/` directory
3. Run: `python3 pptx_to_video.py --background input/your-background.png`

The slides will be centered and overlaid on your background image.

---

## TypeScript Implementation (For Advanced Users)

### Setup

```bash
# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit .env and add:
# - ELEVENLABS_API_KEY=your_api_key
# - ELEVENLABS_VOICE_ID=your_voice_id
# - BACKGROUND_PATH=input/background.png (optional)
```

### Run

```bash
# One-time build
npm run build

# Watch mode (rebuilds on file changes)
npm run watch
```

### Using Custom Background

Add to your `.env` file:
```
BACKGROUND_PATH=input/background.png
```

Or use the default background included in the repository.

---

## Output

Both implementations create:
- **Final video**: `output/output.mp4`
- **Intermediate files**: `temp/` (Python) or `cache/` (TypeScript)

## Tips

- The default background is a subtle blue gradient
- Backgrounds should be 1920x1080 for best results
- Slides will be automatically centered on the background
- Use `--clean` flag to remove temporary files before processing
