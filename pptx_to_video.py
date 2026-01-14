#!/usr/bin/env python3
"""
PPTX/PDF to Video Pipeline
Converts PowerPoint presentations or PDF files to MP4 video slideshows with voiceover.

Pipeline: PPTX/PDF → PDF → RAW PNG (via pdftoppm) → Audio (TTS) → Individual Videos → Final MP4

This ensures consistent RAW PNG extraction from PDF for all input types.
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path
from gtts import gTTS

try:
    from PyPDF2 import PdfReader
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False


class PPTXToVideoConverter:
    """Main converter class for PPTX/PDF to MP4 pipeline."""
    
    def __init__(self, input_dir="input", output_dir="output", temp_dir="temp", background_path=None):
        """
        Initialize the converter.
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.temp_dir = Path(temp_dir)
        self.background_path = Path(background_path) if background_path else None
        
        # Create subdirectories
        self.pdf_dir = self.temp_dir / "pdf"
        self.slides_dir = self.temp_dir / "slides"
        self.audio_dir = self.temp_dir / "audio"
        self.videos_dir = self.temp_dir / "slide_videos"
        
        # Ensure directories exist
        for directory in [self.output_dir, self.temp_dir, self.pdf_dir,
                         self.slides_dir, self.audio_dir, self.videos_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def check_dependencies(self):
        """Check if required external tools are available."""
        # Check for FFmpeg
        try:
            subprocess.run(["ffmpeg", "-version"], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL, 
                         check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERROR: FFmpeg is not installed or not in PATH")
            sys.exit(1)
        
        # Check for pdftoppm
        try:
            subprocess.run(["pdftoppm", "-v"], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL, 
                         check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERROR: pdftoppm is not installed.")
            sys.exit(1)
        
        # Check for LibreOffice
        try:
            subprocess.run(["soffice", "--version"], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL, 
                         check=True)
            self.has_libreoffice = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.has_libreoffice = False
            # Warning only, as user might input PDF directly
    
    def convert_pptx_to_pdf(self, pptx_path):
        """Convert PPTX to PDF using LibreOffice."""
        print("Converting PPTX to PDF using LibreOffice...")
        
        pdf_path = self.pdf_dir / "input.pdf"
        
        cmd = [
            "soffice", "--headless", "--convert-to", "pdf",
            "--outdir", str(self.pdf_dir), str(pptx_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"ERROR: LibreOffice conversion failed: {e}")
            sys.exit(1)
        
        generated_pdf = self.pdf_dir / f"{pptx_path.stem}.pdf"
        if generated_pdf.exists() and generated_pdf != pdf_path:
            generated_pdf.rename(pdf_path)
        
        if not pdf_path.exists():
            print(f"ERROR: PDF was not created at {pdf_path}")
            sys.exit(1)
        
        print(f"  Created: {pdf_path}")
        return pdf_path
    
    def convert_pdf_to_png(self, pdf_path):
        """Convert PDF pages to RAW PNG images using pdftoppm."""
        print("Converting PDF to RAW PNG images using pdftoppm...")
        
        try:
            cmd = [
                "pdftoppm", "-png", "-r", "300",
                str(pdf_path), str(self.slides_dir / "slide")
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            
            png_files = sorted(self.slides_dir.glob("slide-*.png"))
            
            if not png_files:
                print("ERROR: No PNG files were generated")
                sys.exit(1)
            
            print(f"  Converted {len(png_files)} pages to PNG")
            return png_files
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"ERROR: Failed to convert PDF to PNG: {e}")
            sys.exit(1)
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text from PDF pages using pdfplumber (recommended) or PyPDF2.
        """
        texts = []
        
        # OPSI 1: Coba pakai pdfplumber (Lebih Akurat)
        try:
            import pdfplumber
            print("   [Metode] Menggunakan pdfplumber untuk ekstraksi teks...")
            
            with pdfplumber.open(str(pdf_path)) as pdf:
                for i, page in enumerate(pdf.pages):
                    # Extract text
                    text = page.extract_text() or ""
                    
                    # Bersihkan text dari spasi berlebih
                    text = text.strip()
                    
                    # Debug print untuk melihat apakah teks terbaca
                    preview = text[:50].replace('\n', ' ') + "..." if len(text) > 50 else text
                    print(f"    - Slide {i+1}: {len(text)} karakter ditemukan. ('{preview}')")
                    
                    texts.append(text)
            return texts

        except ImportError:
            print("   [!] Library 'pdfplumber' tidak ditemukan.")
            print("       Saran: Install dengan 'pip install pdfplumber' untuk hasil lebih baik.")
            print("   [Metode] Fallback ke PyPDF2...")

        # OPSI 2: Fallback ke PyPDF2 (Bawaan)
        if not HAS_PYPDF2:
            print("Warning: PyPDF2 not installed. Cannot extract text.")
            return []
        
        try:
            reader = PdfReader(str(pdf_path))
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                text = text.strip()
                print(f"    - Slide {i+1} (PyPDF2): {len(text)} chars found.")
                texts.append(text)
            return texts
        except Exception as e:
            print(f"Error extracting text: {e}")
            return []
        
    def create_silent_audio(self, audio_path, duration=2.0):
        """Create a silent audio file using FFmpeg."""
        cmd = [
            "ffmpeg", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo",
            "-t", str(duration), "-q:a", "9", "-acodec", "libmp3lame",
            "-y", str(audio_path)
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return audio_path
        except subprocess.CalledProcessError:
            return None
    
    def concatenate_videos(self, video_paths):
        """Concatenate all slide videos into final output using FFmpeg concat."""
        output_path = self.output_dir / "output.mp4"
        concat_file = self.temp_dir / "slides_list.txt"
        
        with open(concat_file, "w") as f:
            for video_path in video_paths:
                f.write(f"file '{video_path.absolute()}'\n")
        
        cmd = [
            "ffmpeg", "-f", "concat", "-safe", "0",
            "-i", str(concat_file), "-c", "copy", "-y", str(output_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"\n✓ Final video created: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to concatenate videos: {e}")
            sys.exit(1)
    
    def process(self, input_filename="test.pdf", language='en'):
        """Main processing pipeline."""
        input_path = self.input_dir / input_filename
        
        if not input_path.exists():
            print(f"ERROR: Input file not found: {input_path}")
            sys.exit(1)
        
        is_pdf = input_path.suffix.lower() == '.pdf'
        
        print(f"Processing: {input_path}")
        self.check_dependencies()
        
        # Step 1: Get or convert to PDF
        if is_pdf:
            print("\n1. Using input PDF file...")
            pdf_path = self.pdf_dir / "input.pdf"
            shutil.copy2(input_path, pdf_path)
        else:
            print("\n1. Converting PPTX to PDF...")
            pdf_path = self.convert_pptx_to_pdf(input_path)
        
        # Step 2: Extract text
        print("\n2. Extracting text from PDF...")
        slide_texts = self.extract_text_from_pdf(pdf_path)
        
        # Step 3: Convert to PNG
        print("\n3. Extracting RAW PNG images from PDF...")
        png_files = self.convert_pdf_to_png(pdf_path)
        
        # Fallback text logic
        if not slide_texts or len(slide_texts) != len(png_files):
            print("   Warning: Text mismatch or extraction failed. Using default narration.")
            slide_texts = [f"Slide {i}" for i in range(1, len(png_files) + 1)]
        
        # Step 4: Generate audio for each slide (FORCE LOOP)
        print("\n4. Generating TTS audio for each slide...")
        audio_files = []
        
        for idx, (png_path, text) in enumerate(zip(png_files, slide_texts), 1):
            png_name = png_path.stem
            slide_suffix = png_name.split('-')[-1]
            audio_path = self.audio_dir / f"slide-{slide_suffix}.mp3"
            
            print(f"   Processing Slide {idx}...")
            
            if not text or text.strip() == "":
                text = f"Slide {idx}" # Minimal text to avoid gTTS error
            
            # --- MODIFIED LOGIC: LOOP UNTIL SUCCESS ---
            if not audio_path.exists():
                retry_count = 0
                while True: # Infinite loop until success
                    try:
                        # Jeda preventif (rate limiting)
                        # Semakin banyak slide, semakin penting jeda ini
                        time.sleep(1) 
                        
                        tts = gTTS(text=text, lang=language, slow=False)
                        tts.save(str(audio_path))
                        
                        print(f"     ✓ Audio generated: {audio_path.name}")
                        break # SUKSES -> Keluar dari while
                        
                    except Exception as e:
                        retry_count += 1
                        wait_time = 10 # Detik tunggu kalau gagal
                        
                        print(f"     [!] Gagal generate audio (Percobaan {retry_count}).")
                        print(f"         Error: {e}")
                        print(f"         Menunggu {wait_time} detik sebelum mencoba lagi...")
                        
                        # Tunggu sebelum mencoba lagi agar tidak diblokir
                        time.sleep(wait_time)
            else:
                print(f"     [i] Using existing audio: {audio_path.name}")
            
            audio_files.append(audio_path)
        
        # Step 5: Create Individual Videos
        print("\n5. Creating individual slide videos...")
        video_files = []
        for png_path, audio_path in zip(png_files, audio_files):
            png_name = png_path.stem
            slide_suffix = png_name.split('-')[-1]
            video_path = self.videos_dir / f"slide-{slide_suffix}.mp4"
            
            print(f"   Creating video for {png_name}...")
            
            cmd = [
                "ffmpeg", "-loop", "1", "-i", str(png_path),
                "-i", str(audio_path), 
                "-c:v", "libx264",
                "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", # Memastikan lebar/tinggi genap
                "-tune", "stillimage",
                "-shortest", 
                "-pix_fmt", "yuv420p", 
                "-y", str(video_path)
            ]
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                video_files.append(video_path)
            except subprocess.CalledProcessError as e:
                print(f"  ERROR: Failed to create video. Return code: {e.returncode}")
                try:
                    stderr = e.stderr.decode('utf-8', errors='replace') if e.stderr else ''
                    stdout = e.stdout.decode('utf-8', errors='replace') if e.stdout else ''
                    if stderr:
                        print("  ---- FFmpeg stderr ----")
                        print(stderr)
                    if stdout:
                        print("  ---- FFmpeg stdout ----")
                        print(stdout)
                except Exception:
                    pass
                print(f"  Command: {' '.join(cmd)}")
                sys.exit(1)
        
        # Step 6: Concatenate
        print("\n6. Concatenating all slide videos...")
        final_video = self.concatenate_videos(video_files)
        
        print("\n" + "=" * 60)
        print("✓ PIPELINE COMPLETED SUCCESSFULLY!")
        print(f"✓ Output video: {final_video}")
        print("=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Convert PPTX/PDF to MP4")
    parser.add_argument("--input", "-i", default="input")
    parser.add_argument("--output", "-o", default="output")
    parser.add_argument("--temp", "-t", default="temp")
    parser.add_argument("--file", "-f", default="slides.pptx")
    parser.add_argument("--pptx", "-p", default=None)
    parser.add_argument("--language", "-l", default="en")
    parser.add_argument("--background", "-b", default=None)
    parser.add_argument("--clean", action="store_true")
    
    args = parser.parse_args()
    
    input_file = args.pptx if args.pptx else args.file
    
    if args.clean:
        if Path(args.temp).exists():
            shutil.rmtree(args.temp)
            
    converter = PPTXToVideoConverter(
        input_dir=args.input, output_dir=args.output,
        temp_dir=args.temp, background_path=args.background
    )
    converter.process(input_filename=input_file, language=args.language)

if __name__ == "__main__":
    main()