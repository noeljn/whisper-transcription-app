import os
import warnings
from transformers import pipeline
from pydub import AudioSegment
import tempfile

def transcribe_audio(audio_file):
    ALLOWED_FORMATS = [".mp3", ".wav", ".flac"]

    # Suppress warnings
    warnings.filterwarnings("ignore")

    # Check if the audio file exists
    if not os.path.isfile(audio_file):
        raise FileNotFoundError(f"The audio file '{audio_file}' does not exist.")

    # Create a temporary file to store the converted audio
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file)[1])

    if not any(audio_file.endswith(ext) for ext in ALLOWED_FORMATS):
        # Convert the audio file to a supported format if possible
        try:
            ext = ALLOWED_FORMATS[0]
            print(f"Converting {audio_file} to {ext}...")
            # Convert the audio file to the supported format
            audio = AudioSegment.from_file(audio_file)
            audio.export(temp_file.name, format=ext.lstrip('.'))
            audio_file = temp_file.name
        except Exception as e:
            raise RuntimeError(f"Failed to convert audio file to a supported format. Error: {e}")

    # Model ID for KBLab kb-whisper-medium
    model_id = "KBLab/kb-whisper-medium"

    # Create the ASR pipeline
    asr_pipeline = pipeline(
        "automatic-speech-recognition",
        model=model_id,
        chunk_length_s=30,
        device="cpu"
    )

    # Suppress specific warnings during transcription
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # Perform transcription
        result = asr_pipeline(audio_file)

    # The result will be a dictionary with the transcribed text
    transcribed_text = result["text"]
    print("Transcribed text:", transcribed_text)

    # Clean up the temporary file
    os.remove(temp_file.name)

    return transcribed_text
