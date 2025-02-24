import sys
import os
import warnings
from transformers import pipeline

# Suppress warnings
warnings.filterwarnings("ignore")

# Check if the correct number of arguments are provided
if len(sys.argv) != 3:
    print("Usage: python run.py <audio_file> <output_location>")
    sys.exit(1)

# Get the audio file and output location from command-line arguments
audio_file = sys.argv[1]
output_location = sys.argv[2]

# Check if the audio file exists
if not os.path.isfile(audio_file):
    print(f"Error: The audio file '{audio_file}' does not exist.")
    sys.exit(1)

# Check if the audio file is m4a and convert to mp3 if needed
if audio_file.lower().endswith('.m4a'):
    from pydub import AudioSegment
    # Create mp3 filename by replacing extension
    mp3_file = os.path.splitext(audio_file)[0] + '.mp3'
    # Convert m4a to mp3
    audio = AudioSegment.from_file(audio_file, format="m4a")
    audio.export(mp3_file, format="mp3")
    # Update audio_file to use the mp3 version
    audio_file = mp3_file


# Check if the output location is a directory
if os.path.isdir(output_location):
    output_location = os.path.join(output_location, "transcription.txt")

# Check if the output directory exists
output_dir = os.path.dirname(output_location)
if output_dir and not os.path.exists(output_dir):
    print(f"Error: The output directory '{output_dir}' does not exist.")
    sys.exit(1)

# Model ID for KBLab kb-whisper-medium
model_id = "KBLab/kb-whisper-medium"

# Create the ASR pipeline
asr_pipeline = pipeline(
    "automatic-speech-recognition",
    model=model_id,
    chunk_length_s=30,
    device="mps"
)

# Suppress specific warnings during transcription
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    # Perform transcription
    result = asr_pipeline(audio_file)

# The result will be a dictionary with the transcribed text
transcribed_text = result["text"]
print("Transcribed text:", transcribed_text)

# Write the transcribed text to the specified output location
with open(output_location, 'w') as f:
    f.write(transcribed_text)
