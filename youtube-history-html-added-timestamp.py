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

# ==============================
# CONFIG
# ==============================
FILE_PATH = "watch-history.html"   # <-- Your Takeout HTML file

# ==============================
# FUNCTIONS
# ==============================

def load_youtube_history_from_html(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    records = []

    for div in soup.find_all("div", class_="content-cell"):
        try:
            links = div.find_all("a")
            text = div.get_text(" ", strip=True)

            title = None
            url = None
            channel = "Unknown"
            watch_time = None

            # Find video link
            for a in links:
                if "watch" in a.get("href", ""):
                    title = a.text.strip()
                    url = a["href"]

                if "channel" in a.get("href", "") or "@" in a.get("href", ""):
                    channel = a.text.strip()

            # Find date
            # Example: 12 Jan 2026, 22:50:28 GMT
            for part in text.split(" "):
                pass

            # Extract date using regex-like approach
            import re
            match = re.search(r"\d{1,2} \w{3} \d{4}, \d{2}:\d{2}:\d{2}", text)
            if match:
                watch_time = datetime.strptime(match.group(0), "%d %b %Y, %H:%M:%S")

            if title and url and watch_time:
                records.append({
                    "title": title,
                    "url": url,
                    "channel": channel,
                    "time": watch_time
                })

        except Exception:
            continue

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
    print(f"✅ Saved: {filename}")


def save_filtered_excel(df, start_date, end_date):
    start_fmt = pd.to_datetime(start_date, dayfirst=True).strftime("%Y-%m-%d")
    end_fmt = pd.to_datetime(end_date, dayfirst=True).strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    filename = f"youtube-history-{start_fmt}-to-{end_fmt}-{timestamp}.xlsx"
    df.to_excel(filename, index=False)
    print(f"✅ Saved: {filename}")


# ==============================
# MAIN
# ==============================

print("📺 Select one option:")
print("1. YouTube full history")
print("2. YouTube filtered history")
print("3. Both full and filtered history")

choice = input("Enter choice (1/2/3): ").strip()

print("📂 Loading YouTube history from HTML...")
history_df = load_youtube_history_from_html(FILE_PATH)

print(f"✅ Loaded {len(history_df)} records")

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
    print("❌ Invalid choice")
