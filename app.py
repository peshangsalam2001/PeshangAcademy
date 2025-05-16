from flask import Flask, request, send_file, render_template_string
from pytube import YouTube
import os
import tempfile
import subprocess

app = Flask(__name__)

# Simple homepage with form
HTML = """
<!doctype html>
<title>YouTube Downloader</title>
<h2>Download YouTube Video</h2>
<form method=post>
  YouTube URL: <input type=text name=url size=60 required><br><br>
  Cookies (optional, paste your cookies.txt content):<br>
  <textarea name=cookies rows=6 cols=60></textarea><br><br>
  <input type=submit value=Download>
</form>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        cookies_text = request.form.get('cookies', '').strip()

        try:
            # Save cookies to temp file if provided
            cookies_file = None
            if cookies_text:
                cookies_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
                cookies_file.write(cookies_text.encode('utf-8'))
                cookies_file.close()

            # Initialize YouTube object with cookies if any
            yt = YouTube(url, cookies=cookies_file.name if cookies_file else None)

            # Select highest resolution progressive stream (audio+video)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

            if not stream:
                return "No suitable progressive stream found.", 400

            # Download to temp file
            temp_dir = tempfile.mkdtemp()
            video_path = stream.download(output_path=temp_dir)

            # Clean up cookies file
            if cookies_file:
                os.unlink(cookies_file.name)

            # Send file to user
            return send_file(video_path, as_attachment=True, download_name=f"{yt.title}.mp4")

        except Exception as e:
            return f"Error: {e}", 500

    return render_template_string(HTML)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
