from flask import Flask, request, send_file, jsonify
import yt_dlp
import os

app = Flask(__name__)
os.makedirs("downloads", exist_ok=True)

quality_map = {
    "4k": "bestvideo[height<=2160]+bestaudio/best",
    "2k": "bestvideo[height<=1440]+bestaudio/best",
    "1080p": "bestvideo[height<=1080]+bestaudio/best",
    "audio": "bestaudio"
}

@app.route("/download", methods=["POST"])
def download_video():
    data = request.get_json()
    url = data.get("url")
    quality = data.get("quality", "1080p").lower()

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    ydl_opts = {
        'format': quality_map.get(quality, "best"),
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }] if quality == "audio" else [{
            'key': 'FFmpegVideoConvertor',
            'preferredformat': 'mp4'
        }]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if quality == "audio":
                filename = filename.rsplit(".", 1)[0] + ".mp3"

        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def index():
    return "✅ YouTube Downloader API is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
