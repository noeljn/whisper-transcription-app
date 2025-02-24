from flask import Flask, request, render_template, session, redirect, url_for, Response
from src.whisper import transcribe_audio

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

@app.route("/", methods=["GET", "POST"])
def index():
    transcription = None

    if request.method == "POST":
        audio_file = request.files.get("audio_file")

        if audio_file:
            file_path = f"/tmp/{audio_file.filename}"
            audio_file.save(file_path)
            
            try:
                # Pass file_path instead of audio_file
                text = transcribe_audio(file_path)

                # Store transcription in session
                session['transcription'] = text

                # Refresh the page
                return redirect(url_for("index"))
            except Exception as e:
                transcription = f"Error: {str(e)}"
                session['transcription'] = transcription
                return redirect(url_for("index"))
        else:
            transcription = "No file uploaded."

        session['transcription'] = transcription
        return redirect(url_for("index"))


    # If we get here via GET or after redirect, fetch the session transcription
    transcription = session.get('transcription', None)
    return render_template("index.html", transcription=transcription)


@app.route("/download")
def download_text():
    """
    Serve the transcription text as a downloadable .txt file
    """
    transcription = session.get('transcription', '')
    # If there's nothing in the session, provide an empty string
    # Return as a text/plain response with a Content-Disposition header
    return Response(
        transcription,
        mimetype="text/plain",
        headers={"Content-disposition": "attachment; filename=transcription.txt"}
    )


if __name__ == "__main__":
    # Make it visible on your LAN
    app.run(host="0.0.0.0", port=5001, debug=True)
