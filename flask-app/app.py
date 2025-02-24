from flask import Flask, request, render_template, session, redirect, url_for, Response
from src.whisper import transcribe_audio
import tempfile
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

@app.route("/", methods=["GET", "POST"])
def index():
    transcription = None

    if request.method == "POST":
        audio_file = request.files.get("audio_file")

        if audio_file:
            # Create a temporary directory
            temp_dir = tempfile.mkdtemp()
            temp_path = os.path.join(temp_dir, audio_file.filename)
            audio_file.save(temp_path)
            try:
                text = transcribe_audio(temp_path)
                os.unlink(temp_path)  # Clean up the temporary file
                os.rmdir(temp_dir)    # Remove the temporary directory
                session['transcription'] = text
                return redirect(url_for("index"))
            except Exception as e:
                try:
                    os.unlink(temp_path)  # Attempt to clean up even on error
                    os.rmdir(temp_dir)    # Remove the temporary directory
                except:
                    pass  # Ignore cleanup errors
                transcription = f"Error: {str(e)}"
                session['transcription'] = transcription
                return redirect(url_for("index"))
        else:
            transcription = "No file uploaded."
            session['transcription'] = transcription
            return redirect(url_for("index"))

    transcription = session.get('transcription', None)
    return render_template("index.html", transcription=transcription)


@app.route("/download")
def download_text():
    transcription = session.get('transcription', '')
    return Response(
        transcription,
        mimetype="text/plain",
        headers={"Content-disposition": "attachment; filename=transcription.txt"}
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
