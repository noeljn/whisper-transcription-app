from flask import Flask, request, render_template, session, redirect, url_for, Response
from redis import Redis
from rq import Queue
from rq.job import Job
import os
import tempfile

# Import the RQ task
from tasks import transcribe_task

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_for_session'

# Set up Redis and RQ
redis_conn = Redis(host='localhost', port=6379)  # Adjust if your Redis is elsewhere
q = Queue('default', connection=redis_conn)

@app.route("/", methods=["GET", "POST"])
def index():
    transcription = None
    job_id = None

    if request.method == "POST":
        audio_file = request.files.get("audio_file")
        if audio_file:
            # Save file to a temp location
            # Make sure /tmp is writable or choose a different temp location
            tmp_dir = tempfile.gettempdir()
            file_path = os.path.join(tmp_dir, audio_file.filename)
            audio_file.save(file_path)

            # Enqueue the transcription job
            job = q.enqueue(transcribe_task, file_path)
            job_id = job.get_id()

            # Store job_id in session or pass as a query param
            session['job_id'] = job_id

            return redirect(url_for("index"))

    # If we already have a job_id from a previous submission, check status
    if 'job_id' in session:
        job_id = session['job_id']
        job = Job.fetch(job_id, connection=redis_conn)

        if job.is_finished:
            # job.result is the transcription from transcribe_task
            transcription = job.result
        elif job.is_failed:
            transcription = f"Job failed: {job.exc_info}"
        else:
            transcription = "Transcription in progress..."

    return render_template("index.html", transcription=transcription, job_id=job_id)


@app.route("/download")
def download_text():
    """
    Serve the transcription text as a downloadable .txt file
    """
    # If a job ID is in session, get the result
    job_id = session.get('job_id', None)
    if not job_id:
        return "No job found", 400

    job = Job.fetch(job_id, connection=redis_conn)
    if job.is_finished:
        transcription = job.result or ""
    else:
        # If it's not finished or failed, handle accordingly
        return "Transcription not available yet", 400

    return Response(
        transcription,
        mimetype="text/plain",
        headers={"Content-disposition": "attachment; filename=transcription.txt"}
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
