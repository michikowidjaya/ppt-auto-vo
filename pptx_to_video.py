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
        
        Args:
            input_dir: Directory containing input files (PPTX/PDF and INSTRUKSI.txt)
            output_dir: Directory for output video
            temp_dir: Temporary directory for intermediate files
            background_path: (Deprecated) No longer used
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
            print("Please install FFmpeg: https://ffmpeg.org/download.html")
            sys.exit(1)
        
        # Check for pdftoppm (required for PDF to PNG conversion)
        try:
            subprocess.run(["pdftoppm", "-v"], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL, 
                         check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERROR: pdftoppm is not installed or not in PATH")
            print("Please install poppler-utils:")
            print("  Ubuntu/Debian: sudo apt install poppler-utils")
            print("  macOS: brew install poppler")
            sys.exit(1)
        
        # Check for LibreOffice (required for PPTX to PDF conversion)
        try:
            subprocess.run(["soffice", "--version"], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL, 
                         check=True)
            self.has_libreoffice = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.has_libreoffice = False
            print("ERROR: LibreOffice not found. Required for PPTX to PDF conversion.")
            print("Please install LibreOffice:")
            print("  Ubuntu/Debian: sudo apt install libreoffice")
            print("  macOS: brew install --cask libreoffice")
            sys.exit(1)
    
    def convert_pptx_to_pdf(self, pptx_path):
        """
        Convert PPTX to PDF using LibreOffice.
        
        Args:
            pptx_path: Path to PPTX file
            
        Returns:
            Path: Path to generated PDF file
        """
        print("Converting PPTX to PDF using LibreOffice...")
        
        # Output PDF path
        pdf_path = self.pdf_dir / "input.pdf"
        
        cmd = [
            "soffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", str(self.pdf_dir),
            str(pptx_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"ERROR: LibreOffice conversion failed: {e}")
            sys.exit(1)
        
        # Rename the output to our expected name (input.pdf)
        generated_pdf = self.pdf_dir / f"{pptx_path.stem}.pdf"
        if generated_pdf.exists() and generated_pdf != pdf_path:
            generated_pdf.rename(pdf_path)
        
        if not pdf_path.exists():
            print(f"ERROR: PDF was not created at {pdf_path}")
            sys.exit(1)
        
        print(f"  Created: {pdf_path}")
        return pdf_path
    
    def convert_pdf_to_png(self, pdf_path):
        """
        Convert PDF pages to RAW PNG images using pdftoppm.
        Each PNG will be a direct representation of the PDF page content.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            list: List of PNG file paths
        """
        print("Converting PDF to RAW PNG images using pdftoppm...")
        
        try:
            cmd = [
                "pdftoppm",
                "-png",
                "-r", "300",
                str(pdf_path),
                str(self.slides_dir / "slide")
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Get list of generated PNGs (pdftoppm creates slide-1.png, slide-2.png, etc.)
            png_files = sorted(self.slides_dir.glob("slide-*.png"))
            
            if not png_files:
                print("ERROR: No PNG files were generated")
                sys.exit(1)
            
            # Rename to our standardized format (slide-1.png, slide-2.png stays as is)
            # This matches the problem statement format
            print(f"  Converted {len(png_files)} pages to PNG")
            for png_file in png_files:
                print(f"    {png_file.name}")
            
            return png_files
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"ERROR: Failed to convert PDF to PNG: {e}")
            print("Make sure pdftoppm (poppler-utils) is installed")
            sys.exit(1)
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text from PDF pages.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            list: List of text content per page
        """
        if not HAS_PYPDF2:
            print("Warning: PyPDF2 not installed. Cannot extract text from PDF.")
            print("Install with: pip install PyPDF2")
            return []
        
        try:
            reader = PdfReader(str(pdf_path))
            texts = []
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text().strip()
                texts.append(text)
                print(f"  Page {page_num}: {text[:100]}..." if len(text) > 100 else f"  Page {page_num}: {text}")
            return texts
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return []
    
    def create_silent_audio(self, audio_path, duration=2.0):
        """
        Create a silent audio file using FFmpeg.
        
        Args:
            audio_path: Output path for audio file
            duration: Duration in seconds
            
        Returns:
            Path: Path to generated audio file
        """
        cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"anullsrc=r=44100:cl=stereo",
            "-t", str(duration),
            "-q:a", "9",
            "-acodec", "libmp3lame",
            "-y",
            str(audio_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return audio_path
        except subprocess.CalledProcessError:
            return None
    
    def concatenate_videos(self, video_paths):
        """
        Concatenate all slide videos into final output using FFmpeg concat.
        Uses the exact FFmpeg command from problem statement.
        
        Args:
            video_paths: List of video file paths
            
        Returns:
            Path: Path to final output video
        """
        output_path = self.output_dir / "output.mp4"
        concat_file = self.temp_dir / "slides_list.txt"
        
        # Create concat file (slides_list.txt as specified in problem statement)
        with open(concat_file, "w") as f:
            for video_path in video_paths:
                f.write(f"file '{video_path.absolute()}'\n")
        
        # FFmpeg command as specified in problem statement
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            "-y",
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"\n✓ Final video created: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to concatenate videos: {e}")
            sys.exit(1)
    
    def process(self, input_filename="slides.pptx", language='en'):
        """
        Main processing pipeline: PPTX/PDF → PDF → RAW PNG → Audio → Video.
        
        This pipeline ensures consistent RAW PNG extraction from PDF for all input types.
        
        Args:
            input_filename: Name of PPTX or PDF file in input directory
            language: Language code for TTS (default: 'en')
        """
        input_path = self.input_dir / input_filename
        
        if not input_path.exists():
            print(f"ERROR: Input file not found: {input_path}")
            sys.exit(1)
        
        # Determine file type
        file_ext = input_path.suffix.lower()
        is_pdf = file_ext == '.pdf'
        is_pptx = file_ext in ['.pptx', '.ppt']
        
        if not is_pdf and not is_pptx:
            print(f"ERROR: Unsupported file type: {file_ext}")
            print("Supported formats: .pptx, .ppt, .pdf")
            sys.exit(1)
        
        print(f"Processing: {input_path}")
        print(f"File type: {'PDF' if is_pdf else 'PPTX'}")
        print("=" * 60)
        
        # Check dependencies
        self.check_dependencies()
        
        # Step 1: Get or convert to PDF
        if is_pdf:
            print("\n1. Using input PDF file...")
            # Copy PDF to temp/pdf/input.pdf
            pdf_path = self.pdf_dir / "input.pdf"
            shutil.copy2(input_path, pdf_path)
            print(f"   Copied to: {pdf_path}")
        else:
            print("\n1. Converting PPTX to PDF...")
            pdf_path = self.convert_pptx_to_pdf(input_path)
        
        # Step 2: Extract text from PDF (for TTS)
        print("\n2. Extracting text from PDF...")
        slide_texts = self.extract_text_from_pdf(pdf_path)
        
        # Step 3: Convert PDF to RAW PNG images
        print("\n3. Extracting RAW PNG images from PDF...")
        png_files = self.convert_pdf_to_png(pdf_path)
        
        # If we couldn't extract text, use default text
        if not slide_texts or len(slide_texts) != len(png_files):
            print("   Warning: Could not extract text from all pages. Using default narration.")
            slide_texts = [f"Slide {i}" for i in range(1, len(png_files) + 1)]
        
        # Step 4: Generate audio for each slide
        print("\n4. Generating TTS audio for each slide...")
        audio_files = []
        for idx, (png_path, text) in enumerate(zip(png_files, slide_texts), 1):
            # Extract slide number from PNG filename (e.g., slide-01.png -> 01)
            png_name = png_path.stem  # Gets "slide-01" from "slide-01.png"
            slide_suffix = png_name.split('-')[-1]  # Gets "01" from "slide-01"
            
            print(f"   Slide {idx}:")
            # Generate audio with the same suffix as the PNG
            audio_path = self.audio_dir / f"slide-{slide_suffix}.mp3"
            
            if not text or text.strip() == "":
                text = f"Slide {idx}"
            
            # Generate or create silent audio
            if not audio_path.exists():
                try:
                    tts = gTTS(text=text, lang=language, slow=False)
                    tts.save(str(audio_path))
                    print(f"  Generated audio: {audio_path.name}")
                except Exception as e:
                    print(f"  Error generating audio: {e}")
                    # Create a silent audio file as fallback
                    audio_path = self.create_silent_audio(audio_path)
            else:
                print(f"  Using existing audio: {audio_path.name}")
            
            audio_files.append(audio_path)
        
        if len(audio_files) != len(png_files):
            print("ERROR: Mismatch between number of slides and audio files")
            sys.exit(1)
        
        # Step 5: Combine PNG and audio into individual videos
        print("\n5. Creating individual slide videos...")
        video_files = []
        for png_path, audio_path in zip(png_files, audio_files):
            # Extract slide suffix from PNG for consistent naming
            png_name = png_path.stem
            slide_suffix = png_name.split('-')[-1]
            print(f"   Processing {png_name}...")
            
            video_path = self.videos_dir / f"slide-{slide_suffix}.mp4"
            
            # FFmpeg command as specified in problem statement
            cmd = [
                "ffmpeg",
                "-loop", "1",
                "-i", str(png_path),
                "-i", str(audio_path),
                "-c:v", "libx264",
                "-shortest",
                "-pix_fmt", "yuv420p",
                "-y",
                str(video_path)
            ]
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                print(f"  Created video: {video_path.name}")
                video_files.append(video_path)
            except subprocess.CalledProcessError as e:
                print(f"  ERROR: Failed to create video: {e}")
                sys.exit(1)
        
        # Step 6: Concatenate all videos into final output
        print("\n6. Concatenating all slide videos into final output...")
        final_video = self.concatenate_videos(video_files)
        
        print("\n" + "=" * 60)
        print("✓ PIPELINE COMPLETED SUCCESSFULLY!")
        print(f"✓ Output video: {final_video}")
        print(f"✓ File size: {final_video.stat().st_size / (1024*1024):.2f} MB")
        print("=" * 60)
        print("\nFolder structure:")
        print(f"  {self.pdf_dir}/input.pdf          # PDF source")
        print(f"  {self.slides_dir}/slide-*.png     # RAW PNG images")
        print(f"  {self.audio_dir}/slide-*.mp3      # TTS audio")
        print(f"  {self.videos_dir}/slide-*.mp4     # Individual videos")
        print(f"  {self.output_dir}/output.mp4      # Final combined video")
        print("=" * 60)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Convert PPTX presentations or PDF files to MP4 video slideshows"
    )
    parser.add_argument(
        "--input", "-i",
        default="input",
        help="Input directory containing PPTX or PDF file (default: input)"
    )
    parser.add_argument(
        "--output", "-o",
        default="output",
        help="Output directory for video (default: output)"
    )
    parser.add_argument(
        "--temp", "-t",
        default="temp",
        help="Temporary directory for intermediate files (default: temp)"
    )
    parser.add_argument(
        "--file", "-f",
        default="slides.pptx",
        help="Name of PPTX or PDF file in input directory (default: slides.pptx)"
    )
    # Keep --pptx for backward compatibility
    parser.add_argument(
        "--pptx", "-p",
        default=None,
        help="(Deprecated: use --file) Name of PPTX file in input directory"
    )
    parser.add_argument(
        "--language", "-l",
        default="en",
        help="Language code for TTS (default: en, use 'id' for Indonesian)"
    )
    parser.add_argument(
        "--background", "-b",
        default=None,
        help="Path to background PNG image to overlay on slides (default: None)"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean temporary directory before processing"
    )
    
    args = parser.parse_args()
    
    # Use --pptx if provided for backward compatibility, otherwise use --file
    input_file = args.pptx if args.pptx else args.file
    
    # Clean temp directory if requested
    if args.clean:
        temp_path = Path(args.temp)
        if temp_path.exists():
            print(f"Cleaning temporary directory: {temp_path}")
            shutil.rmtree(temp_path)
    
    # Create converter and process
    converter = PPTXToVideoConverter(
        input_dir=args.input,
        output_dir=args.output,
        temp_dir=args.temp,
        background_path=args.background
    )
    
    converter.process(input_filename=input_file, language=args.language)


if __name__ == "__main__":
    main()
