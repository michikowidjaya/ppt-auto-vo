# ppt-auto-vo

Automated pipeline untuk mengonversi file PPTX atau PDF menjadi video slideshow (MP4) dengan voiceover.

## Two Implementations Available

### 1. Python Implementation (NEW) ⭐ Recommended for Beginners

**Pipeline:** PPTX/PDF → Extract text & backgrounds → Generate PNG slides → TTS with gTTS → Combine with FFmpeg → output.mp4

**Features:**
- ✅ Free TTS using Google Text-to-Speech (gTTS)
- ✅ No API key required
- ✅ Simple Python setup
- ✅ Automatic fallback to silent audio if offline
- ✅ **Support for PDF files** - Convert PDF documents directly to video
- ✅ **Support for PPTX files** - Convert PowerPoint presentations to video
- ✅ **Dynamic background extraction** - Extract and use background from each slide (PPTX only)
- ✅ **Text overlay rendering** - Render text shapes on backgrounds using Pillow (PPTX only)

**Requirements:**
- Python 3.8+
- FFmpeg
- pdftoppm (poppler-utils) - required for PDF conversion
- LibreOffice (optional, for better PPTX slide rendering)

**Quick Start:**
```bash
# Install dependencies
pip install -r requirements.txt

# Run pipeline with PPTX
python3 pptx_to_video.py

# Run pipeline with PDF
python3 pptx_to_video.py --file Tugas.pdf

# Or use the helper script
./run_pipeline.sh
```

**Documentation:** See [README_PYTHON.md](README_PYTHON.md) for detailed documentation.

---

### 2. TypeScript Implementation (Original)

**Pipeline:** PPTX + INSTRUKSI.txt → (LibreOffice) PDF → (pdftoppm) PNG → (ElevenLabs API) TTS → (FFmpeg) render → output.mp4

**Features:**
- ✅ High-quality TTS using ElevenLabs API
- ✅ Multi-voice support
- ✅ Watch mode for development
- ✅ **Background PNG overlay** - Add custom background to every slide

**Requirements:**
- Node.js 18+
- FFmpeg (ffmpeg + ffprobe)
- LibreOffice (soffice)
- Poppler (pdftoppm)
- ElevenLabs API key (paid)

**Setup:**
```bash
npm i
cp .env.example .env
# Edit .env and add your ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID
# Optionally add BACKGROUND_PATH for custom background image
```

**Run:**
```bash
npm run build    # One-time build
npm run watch    # Watch mode for development
```

---

## Output

Both implementations produce:
- **Final video:** `output/output.mp4`
- **Intermediate files:** `cache/` (TypeScript) or `temp/` (Python)

## Folder Structure

```
project-root/
├── input/
│   ├── slides.pptx          # Your PowerPoint file
│   ├── Tugas.pdf             # Or your PDF file
│   ├── background.png        # (Optional) Default background image
│   └── INSTRUKSI.txt         # (Optional) Instructions
├── output/
│   └── output.mp4            # Final video output
├── temp/                     # Python implementation cache
│   ├── slides/              # PNG slides
│   ├── audio/               # MP3 audio files
│   └── slide_videos/        # Per-slide videos
├── cache/                    # TypeScript implementation cache
├── pptx_to_video.py         # Python implementation
├── run_pipeline.sh          # Python helper script
└── src/                     # TypeScript implementation
```

## Which Implementation to Use?

**Choose Python if:**
- You want a free solution (no API costs)
- You prefer Python
- You don't need high-quality voice synthesis
- You want simpler setup

**Choose TypeScript if:**
- You need professional-quality voiceover
- You have an ElevenLabs API key
- You're already familiar with Node.js
- You need watch mode for iterative development
