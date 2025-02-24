import os
import warnings
from transformers import pipeline
from pydub import AudioSegment
import tempfile
import yaml

def transcribe_audio(audio_file):
    ALLOWED_FORMATS = [".mp3", ".wav", ".flac"]

    # Load configuration
    with open('../config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    whisper_config = config.get('whisper', {})
    model_id = whisper_config.get('model_id', 'KBLab/kb-whisper-medium')
    device = whisper_config.get('device', 'cpu')
    chunk_length_s = whisper_config.get('chunk_length_s', 30)

    # Suppress warnings
    warnings.filterwarnings("ignore")

    # Check if the audio file exists
    if not os.path.isfile(audio_file):
        raise FileNotFoundError(f"The audio file '{audio_file}' does not exist.")

    # Create a temporary file to store the converted audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file)[1]) as temp_file:
        temp_file_path = temp_file.name
        
        if not any(audio_file.endswith(ext) for ext in ALLOWED_FORMATS):
            # Convert the audio file to a supported format if possible
            try:
                ext = ALLOWED_FORMATS[0]
                print(f"Converting {audio_file} to {ext}...")
                # Convert the audio file to the supported format
                audio = AudioSegment.from_file(audio_file)
                audio.export(temp_file_path, format=ext.lstrip('.'))
                audio_file = temp_file_path
            except Exception as e:
                os.unlink(temp_file_path)  # Clean up on error
                raise RuntimeError(f"Failed to convert audio file to a supported format. Error: {e}")

    # Create the ASR pipeline
    asr_pipeline = pipeline(
        "automatic-speech-recognition",
        model=model_id,
        chunk_length_s=chunk_length_s,
        device=device
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
    try:
        os.unlink(temp_file_path)
    except Exception as e:
        print(f"Warning: Failed to delete temporary file {temp_file_path}: {e}")

    return transcribed_text
