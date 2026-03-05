import subprocess

url = "https://www.youtube.com/watch?v=KLRwRSyybdM"
output_path = r"C:\Users\madna\Downloads\Nitin-AWS-Data-Engineering"  # Change as needed

subprocess.run([
    "python", "-m", "yt_dlp",
    url,
    "-P", output_path
])
