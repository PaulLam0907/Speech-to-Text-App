"""
setup.py

A compilation script
for cx_Freeze to include custom .py scripts
to package and build .exe app
"""

import os
import sys
import torch  # for whisper
import torchgen  # for whisper
from cx_Freeze import setup, Executable  # cx-Freeze

# 1. Get the absolute path to where torch is installed in your virtual environment
torch_dir = os.path.dirname(torch.__file__)
torchgen_dir = os.path.dirname(torchgen.__file__)

# Target the wrapper execution file
executable = [Executable("main.py", target_name = "SpeechToTextApp.exe")]

# Include your main UI, isolated backend script, and ffmpeg binary
build_exe_options = {
    "packages": [
        "streamlit",
        "pyarrow",
        "pyarrow.vendored.version",
        
        "whisper",
        "tqdm",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.protocols.websockets.wsproto_impl",
        "uvicorn.loops.auto",
        "uvicorn.loops.asyncio",
        "uvicorn.lifespan.on",
        "uvicorn.lifespan.off",
    ],
    "excludes": ["torch"],
    "include_files": [
        ("app.py", "app.py"),
        ("transcribe.py", "transcribe.py"),
        ("ffmpeg.exe", "ffmpeg.exe"),
        (torch_dir, "lib/torch"),  # copy the entire torch library safely without parsing it
        (torchgen_dir, "lib/torchgen")  # direct injection of torchgen
    ],
    # Disable zip compression so app.py remains a loose file
    "zip_include_packages": [],
    "zip_exclude_packages": "*",
}

setup(
        name = "SpeechToTextApp",
        version = "1.0",
        description = "Local Whisper Video Transcription App",
        options = {"build_exe": build_exe_options},
        executables = executable
)
