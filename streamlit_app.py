import os
import shutil
import subprocess
from pathlib import Path

import streamlit as st
import sys


ROOT = Path(__file__).parent
INPUT_DIR = ROOT / "input"
OUTPUT_DIR = ROOT / "output"
TEMP_DIR = ROOT / "temp"


def ensure_dirs():
    for d in (INPUT_DIR, OUTPUT_DIR, TEMP_DIR):
        d.mkdir(parents=True, exist_ok=True)


def list_input_files():
    return [f.name for f in sorted(INPUT_DIR.glob("*.*")) if f.suffix.lower() in (".pdf", ".pptx")]


def save_uploaded(uploaded_file):
    dest = INPUT_DIR / uploaded_file.name
    with open(dest, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return dest.name


def run_pipeline(filename: str, language: str, clean: bool):
    cmd = [sys.executable, "-u", str(ROOT / "pptx_to_video.py"), "--file", filename, "--output", "output", "--language", language]
    if clean:
        cmd.append("--clean")

    # Run process and capture output (non-streaming fallback)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    out = proc.stdout or ""
    err = proc.stderr or ""
    return proc.returncode, out, err


def main():
    st.title("ppt-auto-vo — Streamlit Frontend")

    ensure_dirs()

    st.sidebar.header("Input")
    uploaded = st.sidebar.file_uploader("Upload PPTX or PDF", type=["pdf", "pptx"])
    if uploaded is not None:
        saved_name = save_uploaded(uploaded)
        st.sidebar.success(f"Saved to input/{saved_name}")

    files = list_input_files()
    if not files:
        st.warning("No input files found in the `input/` directory. Upload one or add files to input/.")
        st.stop()

    selected = st.sidebar.selectbox("Choose input file", files)

    language = st.sidebar.text_input("TTS language code (e.g. en, id)", value="en")
    clean = st.sidebar.checkbox("Clean temp before run", value=True)

    if st.sidebar.button("Run Pipeline"):
        st.info(f"Running pipeline on {selected} (lang={language})")
        log_box = st.empty()
        progress = st.empty()
        with st.spinner("Processing... this may take a while"):
            # Stream subprocess output live
            cmd = [sys.executable, "-u", str(ROOT / "pptx_to_video.py"), "--file", selected, "--output", "output", "--language", language]
            if clean:
                cmd.append("--clean")

            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            lines = []
            try:
                for raw in proc.stdout:
                    line = raw.rstrip()
                    lines.append(line)
                    # Keep last N lines to avoid huge UI
                    last = "\n".join(lines[-1000:])
                    log_box.code(last)
            except Exception as e:
                lines.append(f"[streaming error] {e}")
                log_box.code("\n".join(lines[-1000:]))
            proc.wait()
            code = proc.returncode
            out = "\n".join(lines)
            err = ""

        st.subheader("Process Output")
        if out:
            st.code(out)
        if err:
            st.error("Errors:")
            st.code(err)

        if code == 0:
            st.success("Pipeline finished successfully.")
        else:
            st.error(f"Pipeline exited with code {code}")

        final_video = OUTPUT_DIR / "output.mp4"
        if final_video.exists():
            st.video(str(final_video))
            with open(final_video, "rb") as f:
                btn = st.download_button(label="Download final video", data=f, file_name=final_video.name)
        else:
            st.info("Final video not found in `output/output.mp4`. Check logs above.")


if __name__ == "__main__":
    main()
