import yt_dlp
import os

# Use current directory + downloads folder
current_dir = os.getcwd()
output_path = os.path.join(current_dir, "downloads")
os.makedirs(output_path, exist_ok=True)

# Playlist URL
playlist_url = "https://www.youtube.com/playlist?list=PLXovS_5EZGh6kfcuCxyBG5loBXlJ7cpDE"

ydl_opts = {
    'outtmpl': f'{output_path}/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s',
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([playlist_url])