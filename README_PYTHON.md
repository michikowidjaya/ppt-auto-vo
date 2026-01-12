# Python PPTX/PDF to Video Pipeline

Implementasi pipeline untuk mengonversi file PPTX atau PDF menjadi video slideshow (MP4) dengan voiceover menggunakan Python.

## Fitur

- ✅ **Support PDF** - Konversi file PDF menjadi video dengan voiceover
- ✅ **Support PPTX** - Konversi presentasi PowerPoint menjadi video
- ✅ Ekstraksi teks dari setiap slide/page menggunakan `python-pptx` atau `PyPDF2`
- ✅ Ekstraksi gambar dari slide (jika ada, untuk PPTX)
- ✅ **Ekstraksi background dinamis** - Ekstrak background (warna atau gambar) dari setiap slide (untuk PPTX)
- ✅ **Render teks di atas background** - Overlay teks shapes pada background menggunakan Pillow (untuk PPTX)
- ✅ Konversi slide/page ke format PNG
- ✅ Generate audio voiceover menggunakan Google TTS (`gTTS`)
- ✅ Gabungkan slide dan audio menjadi video per slide
- ✅ Konsolidasikan semua video menjadi satu file output MP4

## Requirements

### System Dependencies

1. **Python 3.8+**
2. **FFmpeg** - untuk encoding video
   ```bash
   # Ubuntu/Debian
   sudo apt install ffmpeg
   
   # macOS
   brew install ffmpeg
   
   # Windows
   # Download dari https://ffmpeg.org/download.html
   ```

3. **pdftoppm (Poppler)** - **REQUIRED** untuk konversi PDF
   ```bash
   # Ubuntu/Debian
   sudo apt install poppler-utils
   
   # macOS
   brew install poppler
   ```

4. **LibreOffice** (opsional, untuk rendering PPTX slide yang lebih baik)
   ```bash
   # Ubuntu/Debian
   sudo apt install libreoffice
   
   # macOS
   brew install --cask libreoffice
   ```

### Python Dependencies

Install Python packages menggunakan pip:

```bash
pip install -r requirements.txt
```

Dependencies yang dibutuhkan:
- `python-pptx`: untuk parsing dan ekstraksi PPTX
- `PyPDF2`: untuk ekstraksi teks dari PDF
- `gTTS`: untuk text-to-speech (Google TTS)
- `Pillow`: untuk manipulasi gambar

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
│   ├── slides.pptx          # File PPTX input (atau)
│   ├── Tugas.pdf             # File PDF input
│   └── INSTRUKSI.txt         # (opsional) instruksi tambahan
├── temp/                     # Folder sementara (auto-generated)
│   ├── slides/
│   │   ├── slide001.png
│   │   ├── slide002.png
│   │   └── ...
│   ├── audio/
│   │   ├── slide001.mp3
│   │   ├── slide002.mp3
│   │   └── ...
│   └── videos/
│       ├── slide001.mp4
│       ├── slide002.mp4
│       └── ...
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
- `--background`, `-b`: **(Deprecated)** No longer used - backgrounds are now extracted from each slide (PPTX only)
- `--clean`: Clean temporary directory before processing

## Pipeline Flow

### For PDF Files:

### 1. Ekstraksi Teks dari PDF
- Menggunakan `PyPDF2` untuk membaca file PDF
- Ekstraksi teks dari setiap page

### 2. Konversi PDF ke PNG
- Menggunakan `pdftoppm` untuk convert setiap page ke PNG
- Resolusi tinggi (300 DPI)
- PNG disimpan di `temp/slides/`

### 3. Generate Audio (TTS)
- Menggunakan `gTTS` untuk convert teks ke MP3
- Audio disimpan di `temp/audio/`
- Jika page tidak ada teks, generate audio default "Page N"

### 4. Combine Page PNG + Audio
- Menggunakan FFmpeg untuk menggabungkan page PNG dengan audio:
  ```bash
  ffmpeg -loop 1 -i slide.png -i audio.mp3 -c:v libx264 -shortest output.mp4
  ```
- Video per page disimpan di `temp/videos/`

### 5. Concatenate Videos
- Menggunakan FFmpeg concat demuxer
- Gabungkan semua video menjadi `output/output.mp4`

---

### For PPTX Files:

### 1. Ekstraksi Teks dan Gambar
- Menggunakan `python-pptx` untuk membaca file PPTX
- Ekstraksi teks dari setiap shape di slide
- Ekstraksi gambar (jika ada) dan simpan di `temp/slides/`

### 2. Ekstraksi Background dan Render Text (python-pptx method)
- **Ekstraksi Background Dinamis**:
  - Ekstrak background (warna solid atau gambar) dari setiap slide
  - Fallback ke background putih jika tidak ada background
  - Setiap slide dapat memiliki background yang berbeda
- **Render Text**:
  - Overlay text shapes di atas background menggunakan Pillow
  - Text wrapping otomatis sesuai lebar shape
  - Font dan ukuran disesuaikan dengan posisi shape

### 3. Generate PNG untuk Setiap Slide
- **Metode 1** (jika LibreOffice tersedia):
  - PPTX → PDF → PNG menggunakan LibreOffice headless
  - Resolusi tinggi (300 DPI)
  - Rendering akurat dengan background dan format asli
- **Metode 2** (fallback - python-pptx + Pillow):
  - Ekstrak background dari slide
  - Render text shapes di atas background
  - Resolusi 1920x1080
  - PNG disimpan di `temp/slides/`

### 4. Generate Audio (TTS)
- Menggunakan `gTTS` untuk convert teks ke MP3
- Audio disimpan di `temp/audio/`
- Jika slide tidak ada teks, generate audio default "Slide N"

### 5. Combine Slide + Audio
- Slide PNG sudah berisi background dan text yang ter-render
- Menggunakan FFmpeg untuk menggabungkan slide dengan audio:
  ```bash
  ffmpeg -loop 1 -i slide.png -i audio.mp3 -c:v libx264 -shortest output.mp4
  ```
- Video per slide disimpan di `temp/videos/`

### 6. Concatenate Videos
- Menggunakan FFmpeg concat demuxer
- Gabungkan semua video menjadi `output/output.mp4`

## Troubleshooting

### FFmpeg not found
```
ERROR: FFmpeg is not installed or not in PATH
```
**Solution**: Install FFmpeg dan pastikan ada di system PATH

### LibreOffice warning
```
WARNING: LibreOffice not found. Will use python-pptx for slide rendering.
```
**Note**: Ini hanya warning. Script akan tetap berjalan menggunakan fallback method.
Untuk hasil lebih baik, install LibreOffice.

### No audio generated
Jika gTTS gagal (misalnya karena masalah koneksi internet), script akan generate silent audio sebagai fallback.

### Low quality slide images
Jika menggunakan fallback method (tanpa LibreOffice), kualitas gambar slide akan lebih rendah.
**Solution**: Install LibreOffice dan pdftoppm untuk hasil terbaik.

## Perbandingan dengan Implementasi TypeScript

Implementasi Python ini adalah alternatif dari implementasi TypeScript yang ada:

| Fitur | TypeScript (existing) | Python (new) |
|-------|----------------------|--------------|
| TTS Engine | ElevenLabs API (berbayar) | gTTS (gratis) |
| Slide Rendering | LibreOffice + pdftoppm | LibreOffice + pdftoppm atau Pillow |
| Dependencies | Node.js, npm | Python, pip |
| Audio Quality | Tinggi (ElevenLabs) | Sedang (Google TTS) |
| Cost | Memerlukan API key | Gratis |
| Internet | Perlu (untuk TTS) | Perlu (untuk TTS) |

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
