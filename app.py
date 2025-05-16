from flask import Flask, request, send_file, render_template_string
from pytube import YouTube
import tempfile
import os

app = Flask(__name__)

COOKIES_FILE_PATH = os.path.join(os.path.dirname(__file__), 'cookies.txt')

HTML = """
<!doctype html>
<title>YouTube Downloader</title>
<h2>Download YouTube Video</h2>
<form method=post>
  YouTube URL: <input type=text name=url size=60 required><br><br>
  <input type=submit value=Download>
</form>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url'].strip()

        try:
            yt = YouTube(url, cookies=COOKIES_FILE_PATH if os.path.exists(COOKIES_FILE_PATH) else None)

            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

            if not stream:
                return "No suitable progressive stream found.", 400

            temp_dir = tempfile.mkdtemp()
            video_path = stream.download(output_path=temp_dir)

            return send_file(video_path, as_attachment=True, download_name=f"{yt.title}.mp4")

        except Exception as e:
            return f"Error: {e}", 500

    return render_template_string(HTML)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
