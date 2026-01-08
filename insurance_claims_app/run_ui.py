#!/usr/bin/env python3
"""
Run the Streamlit frontend
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    ui_path = os.path.join(os.path.dirname(__file__), "ui", "streamlit_app.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", ui_path, "--server.port", "8501"])
