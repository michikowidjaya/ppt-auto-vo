# Python PPTX/PDF to Video Pipeline

Implementasi pipeline untuk mengonversi file PPTX atau PDF menjadi video slideshow (MP4) dengan voiceover menggunakan Python.

## Fitur

- ✅ **Support PDF** - Konversi file PDF menjadi video dengan voiceover
- ✅ **Support PPTX** - Konversi presentasi PowerPoint menjadi video
- ✅ **RAW PNG Extraction** - Ekstraksi gambar slide asli (RAW) dari PDF menggunakan pdftoppm
- ✅ **Unified Pipeline** - Semua input (PPTX/PDF) diproses melalui jalur yang sama: PDF → RAW PNG → Video
- ✅ Ekstraksi teks dari setiap slide/page menggunakan `PyPDF2`
- ✅ Konversi slide/page ke format PNG berkualitas tinggi (300 DPI)
- ✅ Generate audio voiceover menggunakan Google TTS (`gTTS`)
- ✅ Gabungkan slide dan audio menjadi video per slide
- ✅ Konsolidasikan semua video menjadi satu file output MP4

## Requirements

### System Dependencies

1. **Python 3.8+**
2. **FFmpeg** - **REQUIRED** untuk encoding video
   ```bash
   # Ubuntu/Debian
   sudo apt install ffmpeg
   
   # macOS
   brew install ffmpeg
   
   # Windows
   # Download dari https://ffmpeg.org/download.html
   ```

3. **pdftoppm (Poppler)** - **REQUIRED** untuk ekstraksi RAW PNG dari PDF
   ```bash
   # Ubuntu/Debian
   sudo apt install poppler-utils
   
   # macOS
   brew install poppler
   ```

4. **LibreOffice** - **REQUIRED** untuk konversi PPTX ke PDF
   ```bash
   # Ubuntu/Debian
   sudo apt install libreoffice-writer libreoffice-impress
   
   # macOS
   brew install --cask libreoffice
   ```

### Python Dependencies

Install Python packages menggunakan pip:

```bash
pip install -r requirements.txt
```

Dependencies yang dibutuhkan:
- `PyPDF2`: untuk ekstraksi teks dari PDF
- `gTTS`: untuk text-to-speech (Google TTS)

## Instalasi

1. Clone repository:
   ```bash
   git clone <repository-url>
   cd ppt-auto-vo
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Pastikan FFmpeg terinstall:
   ```bash
   ffmpeg -version
   ```

## Struktur Folder

```
project-root/
├── input/
│   ├── file.pptx             # File PPTX input (atau)
│   ├── document.pdf          # File PDF input
│   └── INSTRUKSI.txt         # (opsional) instruksi tambahan
├── temp/                     # Folder sementara (auto-generated)
│   ├── pdf/
│   │   └── input.pdf        # PDF source (converted dari PPTX atau copied dari input)
│   ├── slides/
│   │   ├── slide-1.png      # RAW PNG images dari PDF
│   │   ├── slide-2.png
│   │   └── ...
│   ├── audio/
│   │   ├── slide-1.mp3      # TTS audio untuk setiap slide
│   │   ├── slide-2.mp3
│   │   └── ...
│   ├── slide_videos/
│   │   ├── slide-1.mp4      # Video individual per slide
│   │   ├── slide-2.mp4
│   │   └── ...
│   └── slides_list.txt      # Concatenation list untuk FFmpeg
├── output/
│   └── output.mp4            # Video output final
├── pptx_to_video.py          # Script utama
└── requirements.txt          # Python dependencies
```

## Penggunaan

### Basic Usage

```bash
# Process PPTX file (default)
python pptx_to_video.py

# Process PDF file
python pptx_to_video.py --file Tugas.pdf
```

Script akan:
1. Membaca file dari direktori `input/`
2. Memproses semua slide/pages
3. Generate video output di `output/output.mp4`

### Advanced Options

```bash
# Specify custom input/output directories
python pptx_to_video.py --input ./my-input --output ./my-output

# Specify custom file name (PPTX or PDF)
python pptx_to_video.py --file my-presentation.pptx
python pptx_to_video.py --file Tugas.pdf

# Use Indonesian language for TTS
python pptx_to_video.py --file Tugas.pdf --language id

# Clean temporary files before processing
python pptx_to_video.py --clean

# Show help
python pptx_to_video.py --help
```

### Parameter Options

- `--input`, `-i`: Input directory (default: `input`)
- `--output`, `-o`: Output directory (default: `output`)
- `--temp`, `-t`: Temporary directory (default: `temp`)
- `--file`, `-f`: PPTX or PDF filename (default: `slides.pptx`)
- `--pptx`, `-p`: **(Deprecated)** Use `--file` instead
- `--language`, `-l`: TTS language code (default: `en`)
  - `en`: English
  - `id`: Indonesian
  - `es`: Spanish
  - dll. (lihat [gTTS supported languages](https://gtts.readthedocs.io/en/latest/module.html#languages-gtts-lang))
- `--background`, `-b`: **(Deprecated)** No longer used
- `--clean`: Clean temporary directory before processing

## Pipeline Flow

**Unified Pipeline untuk PPTX dan PDF:**

```
PPTX/PDF Input
    ↓
[Step 1] Convert to PDF (if PPTX) or Copy (if PDF)
    ↓ → temp/pdf/input.pdf
[Step 2] Extract Text from PDF (PyPDF2)
    ↓
[Step 3] Extract RAW PNG from PDF (pdftoppm, 300 DPI)
    ↓ → temp/slides/slide-1.png, slide-2.png, ...
[Step 4] Generate TTS Audio (gTTS)
    ↓ → temp/audio/slide-1.mp3, slide-2.mp3, ...
[Step 5] Combine PNG + Audio (FFmpeg)
    ↓ → temp/slide_videos/slide-1.mp4, slide-2.mp4, ...
[Step 6] Concatenate Videos (FFmpeg concat)
    ↓
output/output.mp4
```

### Detail Setiap Step:

### 1. Convert to PDF (untuk PPTX) / Copy PDF (untuk PDF)
- **PPTX**: Menggunakan LibreOffice headless untuk convert PPTX → PDF
  ```bash
  soffice --headless --convert-to pdf --outdir temp/pdf/ input.pptx
  ```
- **PDF**: Copy file PDF ke `temp/pdf/input.pdf`

### 2. Extract Text dari PDF
- Menggunakan `PyPDF2` untuk membaca file PDF
- Ekstraksi teks dari setiap page untuk TTS
- Jika page tidak ada teks, akan generate default narration "Slide N"

### 3. Extract RAW PNG dari PDF
- Menggunakan `pdftoppm` untuk convert setiap page ke PNG
  ```bash
  pdftoppm -png -r 300 temp/pdf/input.pdf temp/slides/slide
  ```
- Resolusi tinggi (300 DPI) untuk kualitas maksimal
- PNG adalah representasi RAW dari slide tanpa modifikasi
- Output: `slide-1.png`, `slide-2.png`, etc.

### 4. Generate Audio (TTS)
- Menggunakan `gTTS` untuk convert teks ke MP3
- Audio disimpan di `temp/audio/` dengan nama yang match dengan PNG
- Output: `slide-1.mp3`, `slide-2.mp3`, etc.
- Jika gTTS gagal (offline), generate silent audio sebagai fallback

### 5. Combine PNG + Audio
- Menggunakan FFmpeg untuk menggabungkan slide PNG dengan audio:
  ```bash
  ffmpeg -loop 1 -i slide-1.png -i slide-1.mp3 \
         -c:v libx264 -shortest -pix_fmt yuv420p slide-1.mp4
  ```
- Video per slide disimpan di `temp/slide_videos/`

### 6. Concatenate Videos
- Membuat file list: `temp/slides_list.txt`
  ```
  file '/absolute/path/to/slide-1.mp4'
  file '/absolute/path/to/slide-2.mp4'
  ...
  ```
- Menggunakan FFmpeg concat demuxer:
  ```bash
  ffmpeg -f concat -safe 0 -i slides_list.txt -c copy output/output.mp4
  ```
- Gabungkan semua video menjadi `output/output.mp4`

## Troubleshooting

### FFmpeg not found
```
ERROR: FFmpeg is not installed or not in PATH
```
**Solution**: Install FFmpeg dan pastikan ada di system PATH

### pdftoppm not found
```
ERROR: pdftoppm is not installed or not in PATH
```
**Solution**: Install poppler-utils (`sudo apt install poppler-utils` atau `brew install poppler`)

### LibreOffice not found (untuk PPTX)
```
ERROR: LibreOffice not found. Required for PPTX to PDF conversion.
```
**Solution**: Install LibreOffice untuk konversi PPTX. PDF files tidak memerlukan LibreOffice.

### No audio generated
Jika gTTS gagal (misalnya karena masalah koneksi internet), script akan generate silent audio sebagai fallback.

### File naming mismatch
PNG files menggunakan format `slide-1.png`, `slide-2.png`, etc. (sesuai output pdftoppm).
Audio dan video files otomatis match dengan format yang sama.

## Perbandingan dengan Implementasi TypeScript

Implementasi Python ini adalah alternatif dari implementasi TypeScript yang ada:

| Fitur | TypeScript (existing) | Python (new) |
|-------|----------------------|--------------|
| TTS Engine | ElevenLabs API (berbayar) | gTTS (gratis) |
| Slide Rendering | LibreOffice + pdftoppm | LibreOffice + pdftoppm |
| PNG Extraction | RAW dari PDF | RAW dari PDF |
| Dependencies | Node.js, npm | Python, pip |
| Audio Quality | Tinggi (ElevenLabs) | Sedang (Google TTS) |
| Cost | Memerlukan API key | Gratis |
| Internet | Perlu (untuk TTS) | Perlu (untuk TTS) |
| PPTX Support | Via PDF | Via PDF (required LibreOffice) |
| PDF Support | Direct | Direct |

## Examples

### Example 1: Basic PPTX Presentation
```bash
# Buat file input/slides.pptx dengan beberapa slide
python pptx_to_video.py
# Output: output/output.mp4
```

### Example 2: PDF Document
```bash
# Konversi file PDF dengan voiceover
python pptx_to_video.py --file Tugas.pdf --language id
# Output: output/output.mp4
```

### Example 3: Indonesian Presentation
```bash
# Untuk presentasi dalam Bahasa Indonesia
python pptx_to_video.py --language id
```

### Example 4: Custom Paths
```bash
# Gunakan custom directories
python pptx_to_video.py \
  --input ./presentations \
  --file my-slides.pptx \
  --output ./videos \
  --language id
```

## Contributing

Untuk berkontribusi pada project ini:
1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

[Sesuaikan dengan lisensi repository]
