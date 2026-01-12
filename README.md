# ppt-auto-vo

Pipeline: PPTX + INSTRUKSI.txt -> (LibreOffice headless) PDF -> (pdftoppm) PNG per slide -> (ElevenLabs) TTS per slide -> (FFmpeg) render scene per slide -> concat -> output/output.mp4.

Requirements:
- Node.js 18+
- FFmpeg (ffmpeg + ffprobe)
- LibreOffice (soffice)
- Poppler (pdftoppm)

Setup:
1) npm i
2) Copy .env.example to .env
3) Put input/slides.pptx and input/INSTRUKSI.txt

Run:
- npm run build
- npm run watch

Output:
- output/output.mp4
- cache/ for cache files
