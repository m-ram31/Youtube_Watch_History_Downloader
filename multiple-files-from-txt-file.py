import yt_dlp
import os

# Use the full absolute path
output_path = r"C:\Users\madna\Downloads\youtube-downloads\snowflake"
# OR use your OneDrive path if that's where you want them
# output_path = r"C:\Users\madna\OneDrive - Netcompany\Downloads\youtube-downloads"

# Make sure the directory exists
os.makedirs(output_path, exist_ok=True)

ydl_opts = {
    'outtmpl': f'{output_path}/%(title)s.%(ext)s',
}

# Read URLs from file
with open('snowflake.txt', 'r') as file:
    urls = [line.strip() for line in file if line.strip()]

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    for url in urls:
        try:
            print(f"Downloading: {url}")
            ydl.download([url])
            print(f"Successfully downloaded: {url}")
        except Exception as e:
            print(f"Error downloading {url}: {e}")