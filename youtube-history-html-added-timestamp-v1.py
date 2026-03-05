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

# ==============================
# CONFIG
# ==============================
FILE_PATH = "watch-history.html"   # <-- Replace with your file path

# ==============================
# FUNCTIONS
# ==============================

def load_youtube_history_from_html(filepath):
    print("📂 Parsing HTML using lxml parser...")
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml")

    records = []
    divs = soup.find_all("div")

    print(f"🔍 Found {len(divs)} div blocks. Scanning...")

    for i, div in enumerate(divs):
        text = div.get_text(" ", strip=True)
        links = div.find_all("a")

        title = None
        url = None
        channel = "Unknown"
        watch_time = None

        # Extract video title and URL
        for a in links:
            if "watch" in a.get("href", ""):
                title = a.text.strip()
                url = a["href"]
            elif "channel" in a.get("href", "") or "@" in a.get("href", ""):
                channel = a.text.strip()

        # Extract date like '13 Jan 2026, 06:37:37'
        date_match = re.search(r"\d{1,2} \w{3} \d{4}, \d{2}:\d{2}:\d{2}", text)
        if date_match:
            try:
                watch_time = datetime.strptime(date_match.group(0), "%d %b %Y, %H:%M:%S")
            except:
                pass

        if title and url and watch_time:
            records.append({
                "title": title,
                "url": url,
                "channel": channel,
                "time": watch_time
            })

        if i % 100 == 0:
            print(f"  → Processed {i} entries...")

    print(f"✅ Parsed total {len(records)} valid entries.")
    df = pd.DataFrame(records)
    df["date_only"] = df["time"].dt.strftime("%Y-%m-%d")
    return df


def filter_by_date(df, start_date, end_date):
    start = pd.to_datetime(start_date, dayfirst=True)
    end = pd.to_datetime(end_date, dayfirst=True)
    df = df[(df["time"] >= start) & (df["time"] <= end)]
    return df


def save_full_excel(df):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"youtube-full-history-{timestamp}.xlsx"
    df.to_excel(filename, index=False)
    print(f"✅ Saved full history to: {filename}")


def save_filtered_excel(df, start_date, end_date):
    start_fmt = pd.to_datetime(start_date, dayfirst=True).strftime("%Y-%m-%d")
    end_fmt = pd.to_datetime(end_date, dayfirst=True).strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"youtube-history-{start_fmt}-to-{end_fmt}-{timestamp}.xlsx"
    df.to_excel(filename, index=False)
    print(f"✅ Saved filtered history to: {filename}")


# ==============================
# MAIN
# ==============================

print("📺 Select one option:")
print("1. YouTube full history")
print("2. YouTube filtered history")
print("3. Both full and filtered history")

choice = input("Enter choice (1/2/3): ").strip()

# Load data from HTML
history_df = load_youtube_history_from_html(FILE_PATH)

# deduplicate to avoid repeats
history_df = history_df.sort_values(by='time', ascending=False)
history_df = history_df.drop_duplicates(subset='url', keep='first')

# ✅ Remove 'Unknown' channels (ads)
history_df = history_df[history_df['channel'].str.lower() != 'unknown']

if choice == "1":
    save_full_excel(history_df)

elif choice == "2":
    start_date = input("📆 Enter start date (DD-MM-YYYY): ").strip()
    end_date = input("📆 Enter end date (DD-MM-YYYY): ").strip()
    filtered_df = filter_by_date(history_df, start_date, end_date)
    save_filtered_excel(filtered_df, start_date, end_date)

elif choice == "3":
    save_full_excel(history_df)
    start_date = input("📆 Enter start date (DD-MM-YYYY): ").strip()
    end_date = input("📆 Enter end date (DD-MM-YYYY): ").strip()
    filtered_df = filter_by_date(history_df, start_date, end_date)
    save_filtered_excel(filtered_df, start_date, end_date)

else:
    print("❌ Invalid choice. Exiting.")
