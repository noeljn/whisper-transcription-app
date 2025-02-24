# Whisper Transcription App (Flask + RQ + Transformers)

This repository hosts a simple Flask web application that accepts audio file uploads, queues transcription jobs in [Redis Queue (RQ)](https://python-rq.org/), and uses a **Whisper-based** model (via the [Transformers library](https://github.com/huggingface/transformers)) to transcribe the audio in the background.

## Features

- **Upload Audio**: User can upload `.mp3`, `.wav`, `.m4a`, or `.flac` files.
- **Background Jobs**: Jobs are queued in Redis to avoid blocking the main Flask thread.
- **Automatic Speech Recognition**: Uses the `transcribe_audio` function (from `src/whisper.py` or similar) to run KB-Whisper or standard Whisper models.
- **Download Results**: Once transcribed, results can be downloaded as `.txt`.

---

## Prerequisites

1. **Python 3.8+** (or a conda environment with Python 3.8+).
2. **Redis** installed and running:
   - On Ubuntu/Debian:
     ```bash
     sudo apt-get update
     sudo apt-get install redis-server
     sudo service redis-server start
     ```
   - On macOS (with [Homebrew](https://brew.sh/)):
     ```bash
     brew install redis
     redis-server
     ```
3. [**ffmpeg**](https://ffmpeg.org/) installed for `pydub` conversions.
4. Internet connection (if using Hugging Face hub models that need to download weights).

---

## Installation

1. **Clone this repo**:
   ```bash
   git clone https://github.com/noeljn/whisper-transcription-app.git
   cd whisper-transcription-app
   ```

2. **Create and activate a virtual environment (recommended)**:
    ``bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # or
    venv\Scripts\activate.bat  # On Windows
    ````

3. **Install Python dependencies**:
    ```bash
    pip install --upgrade pip  # optional, but recommended
    pip install -r whisper_app/requirements.txt
    ```

## Usage
1. **Start Redis** (if not already running):
   ```bash
   redis-server
   ```

2. **Start the RQ Worker** (in a separate terminal):
   ```bash
   python worker.py
   ```

3. **Start the Flask Application** (in another terminal):
   ```bash
   python app.py
   ```

4. **Access the Web Interface**:
   - Open your browser and go to `http://localhost:5001`
   - Upload an audio file using the interface
   - Wait for transcription to complete
   - Download the results as a text file
