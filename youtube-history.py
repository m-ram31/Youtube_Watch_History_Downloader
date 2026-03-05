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

import json
import pandas as pd
from datetime import datetime
import pytz
import os

# === SETTINGS ===
# FILE_PATH = 'Takeout/YouTube and YouTube Music/history/watch-history.json'  # Adjust as needed
FILE_PATH = 'workstation-ram31-watch-history.json'  # Adjust as needed

# === FUNCTIONS ===

def load_youtube_history(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    watch_entries = []
    for item in data:
        if 'titleUrl' in item:
            watch_entries.append({
                'title': item.get('title'),
                'url': item.get('titleUrl'),
                'channel': item.get('subtitles', [{}])[0].get('name', 'Unknown'),
                'time': item.get('time')
            })
    return pd.DataFrame(watch_entries)

def filter_by_date(df, start_date=None, end_date=None):
    df['time'] = pd.to_datetime(df['time'], format='mixed', errors='coerce')
    utc = pytz.UTC

    if start_date:
        start = pd.to_datetime(start_date, dayfirst=True).replace(tzinfo=utc)
        df = df[df['time'] >= start]

    if end_date:
        end = pd.to_datetime(end_date, dayfirst=True).replace(tzinfo=utc)
        df = df[df['time'] <= end]

    df['date_only'] = df['time'].dt.strftime('%Y-%m-%d')
    return df

def save_filtered_csv(df, start_date, end_date):
    start_fmt = pd.to_datetime(start_date, dayfirst=True).strftime('%Y-%m-%d')
    end_fmt = pd.to_datetime(end_date, dayfirst=True).strftime('%Y-%m-%d')
    filename = f"youtube-history-{start_fmt}-to-{end_fmt}.csv"
    df.to_csv(filename, index=False)
    print(f"✅ Filtered history saved to: {filename}")

# === MAIN MENU ===

print("📺 Select one option:")
print("1. YouTube full history")
print("2. YouTube filtered history")
print("3. Both full and filtered history")

choice = input("Enter choice (1/2/3): ").strip()

# Load full history
print("📂 Loading YouTube watch history...")
history_df = load_youtube_history(FILE_PATH)
history_df['time'] = pd.to_datetime(history_df['time'], format='mixed', errors='coerce')
history_df['date_only'] = history_df['time'].dt.strftime('%Y-%m-%d')

if choice == '1':
    history_df.to_csv("youtube-full-history.csv", index=False)
    print("✅ Full history saved to: youtube-full-history.csv")

elif choice == '2' or choice == '3':
    start_date = input("Enter start date (DD-MM-YYYY): ").strip()
    end_date = input("Enter end date (DD-MM-YYYY): ").strip()

    filtered_df = filter_by_date(history_df.copy(), start_date, end_date)
    save_filtered_csv(filtered_df, start_date, end_date)

    if choice == '3':
        history_df.to_csv("youtube-full-history.csv", index=False)
        print("✅ Full history also saved to: youtube-full-history.csv")

else:
    print("❌ Invalid choice. Exiting.")
