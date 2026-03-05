###########################
#    WORKING COPY
###########################

# STEP 1: Download Your YouTube Data from Google Takeout
# Go to Google Takeout
# Select only YouTube and YouTube Music
# Choose format as .JSON
# Download the archive and extract it — the file you need is usually: /Takeout/YouTube and YouTube Music/history/watch-history.json

# STEP 2: Python Script to Parse the History
# The following script will:
# Load your watch history JSON
# Extract all history or filter by date
# Output to CSV if you want

# Features Added
# Runtime menu for:
# Full history
# Filtered history
# Both
# Filtered output saved with dynamic filename:
# youtube-history-YYYY-MM-DD-to-YYYY-MM-DD.csv
# Adds date_only column in the output

import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re
from collections import Counter

# ========== CONFIGURATION ==========
HTML_FILE = "watch-history.html"             # Input HTML file
IGNORE_FILE = "ignore_channels.txt"          # Optional ignore list
SEARCH_KEYWORDS = []                         # Optional: ["python", "tesla"]
OUTPUT_DIR = r'C:\Users\madna\OneDrive - Netcompany\Documents\Python Scripts\Youtube_Downloader\excel_output_files'                        # Static destination folder
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ========== PARSE HISTORY ==========
def parse_watch_history(html_file, ignore_set=None, keywords=None):
    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml")

    divs = soup.find_all("div")
    entries = []

    for div in divs:
        text = div.get_text(" ", strip=True)
        links = div.find_all("a")

        title = url = None
        channel = "Unknown"
        watch_time = None

        for a in links:
            href = a.get("href", "")
            if "watch" in href:
                title = a.text.strip()
                url = href
            elif "channel" in href or "@" in href:
                channel = a.text.strip()

        match = re.search(r"\d{1,2} \w{3} \d{4}, \d{2}:\d{2}:\d{2}", text)
        if match:
            try:
                watch_time = datetime.strptime(match.group(0), "%d %b %Y, %H:%M:%S")
            except:
                continue

        if title and url and watch_time:
            if channel.lower() == "unknown":
                continue
            if ignore_set and channel.lower() in ignore_set:
                continue
            if keywords and not any(k.lower() in title.lower() for k in keywords):
                continue

            entries.append({
                "title": title,
                "url": url,
                "channel": channel,
                "time": watch_time,
            })

    df = pd.DataFrame(entries)
    df["date_only"] = df["time"].dt.strftime("%Y-%m-%d")
    return df

# ========== FILTER ==========
def filter_by_date(df, start_date, end_date):
    start = pd.to_datetime(start_date, dayfirst=True)
    end = pd.to_datetime(end_date, dayfirst=True)
    return df[(df["time"] >= start) & (df["time"] <= end)]

# ========== EXPORT ==========
def save_to_excel(df, filename_prefix):
    output_path = os.path.join(OUTPUT_DIR, f"{filename_prefix}-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx")
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Monthly sheets
        for month, group in df.groupby(df["time"].dt.strftime('%Y-%m')):
            group.to_excel(writer, sheet_name=month, index=False)

        # Top channels ranking
        top_channels = df["channel"].value_counts().reset_index()
        top_channels.columns = ["Channel", "Count"]
        top_channels.to_excel(writer, sheet_name="Top Channels", index=False)

    print(f"✅ Excel saved: {output_path}")

# ========== IGNORE LIST ==========
def load_ignore_channels(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return set(line.strip().lower() for line in f if line.strip())
    except FileNotFoundError:
        return set()

# ========== MAIN ==========
if __name__ == "__main__":
    print("📺 Select one option:")
    print("1. YouTube full history")
    print("2. YouTube filtered history")
    print("3. Both full and filtered history")
    choice = input("Enter choice (1/2/3): ").strip()

    ignore_channels = load_ignore_channels(IGNORE_FILE)
    df = parse_watch_history(HTML_FILE, ignore_set=ignore_channels, keywords=SEARCH_KEYWORDS)

    if df.empty:
        print("⚠️ No data to write.")
        exit()

    df = df.sort_values("time", ascending=False).drop_duplicates("url")

    if choice == "1":
        save_to_excel(df, "youtube-full-history")

    elif choice == "2":
        start_date = input("📆 Start date (DD-MM-YYYY): ").strip()
        end_date = input("📆 End date (DD-MM-YYYY): ").strip()
        filtered_df = filter_by_date(df, start_date, end_date)
        save_to_excel(filtered_df, f"youtube-history-{start_date}-to-{end_date}")

    elif choice == "3":
        save_to_excel(df, "youtube-full-history")
        start_date = input("📆 Start date (DD-MM-YYYY): ").strip()
        end_date = input("📆 End date (DD-MM-YYYY): ").strip()
        filtered_df = filter_by_date(df, start_date, end_date)
        save_to_excel(filtered_df, f"youtube-history-{start_date}-to-{end_date}")

    else:
        print("❌ Invalid option.")
