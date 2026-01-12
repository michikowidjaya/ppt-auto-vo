# PDF Support Implementation Summary

## Ringkasan Implementasi (Indonesian)

File `pptx_to_video.py` sekarang mendukung konversi file PDF menjadi video dengan voiceover.

### File Yang Mengubah PPT/PDF Jadi Video

**File utama: `pptx_to_video.py`**

File ini adalah implementasi Python yang mengonversi:
- **File PPTX** (PowerPoint) → Video MP4
- **File PDF** (seperti Tugas.pdf) → Video MP4

### Perubahan Yang Dibuat

1. **Menambahkan dukungan PDF**:
   - File `pptx_to_video.py` sekarang dapat mendeteksi file PDF vs PPTX
   - Method baru: `convert_pdf_to_png()` - konversi PDF ke PNG menggunakan pdftoppm
   - Method baru: `extract_text_from_pdf()` - ekstrak teks dari PDF menggunakan PyPDF2

2. **Parameter command-line baru**:
   - `--file` atau `-f`: Tentukan file PPTX atau PDF (menggantikan `--pptx`)
   - `--pptx` masih didukung untuk backward compatibility

3. **Dependencies baru**:
   - `PyPDF2==3.0.1` ditambahkan ke `requirements.txt`
   - `pdftoppm` (poppler-utils) DIPERLUKAN untuk konversi PDF

### Cara Menggunakan

```bash
# Konversi file PDF
python3 pptx_to_video.py --file Tugas.pdf --language id

# Konversi file PPTX (masih berfungsi seperti biasa)
python3 pptx_to_video.py --file slides.pptx --language en

# Menggunakan backward compatibility (PPTX only)
python3 pptx_to_video.py --pptx slides.pptx
```

### Pipeline untuk PDF

1. **Ekstrak teks** dari setiap halaman PDF menggunakan PyPDF2
2. **Konversi PDF ke PNG** untuk setiap halaman menggunakan pdftoppm (300 DPI)
3. **Generate audio** untuk setiap halaman menggunakan Google TTS (gTTS)
4. **Gabungkan PNG + audio** menjadi video per halaman menggunakan FFmpeg
5. **Konkatenasi** semua video menjadi output final

### File Struktur

```
input/
├── slides.pptx          # File PowerPoint
├── Tugas.pdf            # File PDF yang mau diubah
└── test.pdf             # Contoh test file

output/
└── output.mp4           # Video hasil konversi

temp/
├── slides/              # PNG dari setiap halaman/slide
├── audio/               # MP3 audio untuk setiap halaman/slide
└── slide_videos/        # Video per halaman/slide
```

### Instalasi Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# System dependencies (Ubuntu/Debian)
sudo apt-get install ffmpeg poppler-utils

# System dependencies (macOS)
brew install ffmpeg poppler
```

---

## Implementation Summary (English)

The `pptx_to_video.py` file now supports converting PDF files to video with voiceover.

### Which File Converts PPT/PDF to Video?

**Main file: `pptx_to_video.py`**

This is the Python implementation that converts:
- **PPTX files** (PowerPoint) → MP4 video
- **PDF files** (like Tugas.pdf) → MP4 video

### Changes Made

1. **Added PDF support**:
   - `pptx_to_video.py` can now detect PDF vs PPTX files
   - New method: `convert_pdf_to_png()` - converts PDF to PNG using pdftoppm
   - New method: `extract_text_from_pdf()` - extracts text from PDF using PyPDF2

2. **New command-line parameter**:
   - `--file` or `-f`: Specify PPTX or PDF file (replaces `--pptx`)
   - `--pptx` still supported for backward compatibility

3. **New dependencies**:
   - `PyPDF2==3.0.1` added to `requirements.txt`
   - `pdftoppm` (poppler-utils) REQUIRED for PDF conversion

### How to Use

```bash
# Convert PDF file
python3 pptx_to_video.py --file Tugas.pdf --language id

# Convert PPTX file (still works as before)
python3 pptx_to_video.py --file slides.pptx --language en

# Using backward compatibility (PPTX only)
python3 pptx_to_video.py --pptx slides.pptx
```

### Pipeline for PDF

1. **Extract text** from each PDF page using PyPDF2
2. **Convert PDF to PNG** for each page using pdftoppm (300 DPI)
3. **Generate audio** for each page using Google TTS (gTTS)
4. **Combine PNG + audio** into video per page using FFmpeg
5. **Concatenate** all videos into final output

### Tested

- ✅ PDF to video conversion works
- ✅ PPTX to video conversion still works
- ✅ Backward compatibility with `--pptx` parameter
- ✅ Both PDF and PPTX files correctly detected and processed

