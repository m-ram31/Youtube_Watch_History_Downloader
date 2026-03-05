import json
import pandas as pd
from datetime import datetime
import os
from openpyxl import Workbook

# === CONFIGURATION ===
FILE_PATH = 'workstation-ram31-watch-history.json'
IGNORE_FILE = 'ignore_channels.txt'

# === FUNCTIONS ===

def load_ignore_list(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            ignore = [line.strip().lower() for line in f if line.strip()]
        return set(ignore)
    except FileNotFoundError:
        print("⚠️ Ignore list file not found. Continuing without exclusions.")
        return set()

def load_youtube_history(filepath, ignore_set=None):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    watch_entries = []
    for item in data:
        if 'titleUrl' in item:
            channel_name = item.get('subtitles', [{}])[0].get('name', 'Unknown')
            if ignore_set and channel_name.strip().lower() in ignore_set:
                continue
            watch_entries.append({
                'title': item.get('title'),
                'url': item.get('titleUrl'),
                'channel': channel_name,
                'time': item.get('time')
            })
    return pd.DataFrame(watch_entries)

def filter_by_date(df, start_date=None, end_date=None):
    # Parse and normalize time column
    df['time'] = pd.to_datetime(df['time'], format='mixed', errors='coerce', utc=True)
    df['time'] = df['time'].dt.tz_localize(None)  # Make tz-naive

    if start_date:
        start = pd.to_datetime(start_date, dayfirst=True)
        df = df[df['time'] >= start]

    if end_date:
        end = pd.to_datetime(end_date, dayfirst=True)
        df = df[df['time'] <= end]

    df['date_only'] = df['time'].dt.strftime('%Y-%m-%d')
    return df

def save_excel(df, filename):
    if 'time' in df.columns:
        df['time'] = pd.to_datetime(df['time'], errors='coerce')
    df.to_excel(filename, index=False)
    print(f"✅ Saved to: {filename}")

def get_date_range():
    start_date = input("📆 Enter start date (DD-MM-YYYY): ").strip()
    end_date = input("📆 Enter end date (DD-MM-YYYY): ").strip()
    return start_date, end_date

# === MAIN ===

print("📺 Select one option:")
print("1. YouTube full history")
print("2. YouTube filtered history")
print("3. Both full and filtered history")
print("4. Ignore channels with selected dates")
choice = input("Enter choice (1/2/3/4): ").strip()

ignore_set = set()

# Load ignore list only for option 4
if choice == '4':
    ignore_set = load_ignore_list(IGNORE_FILE)

print("📂 Loading YouTube watch history...")
history_df = load_youtube_history(FILE_PATH, ignore_set)

# Parse time safely
history_df['time'] = pd.to_datetime(history_df['time'], format='mixed', errors='coerce', utc=True)
history_df['time'] = history_df['time'].dt.tz_localize(None)
history_df['date_only'] = history_df['time'].dt.strftime('%Y-%m-%d')

# === OPTION HANDLING ===

if choice == '1':
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"youtube-full-history-{timestamp}.xlsx"
    save_excel(history_df, filename)

elif choice == '2':
    start_date, end_date = get_date_range()
    filtered_df = filter_by_date(history_df.copy(), start_date, end_date)
    filename = f"youtube-history-{pd.to_datetime(start_date, dayfirst=True).strftime('%Y-%m-%d')}-to-{pd.to_datetime(end_date, dayfirst=True).strftime('%Y-%m-%d')}.xlsx"
    save_excel(filtered_df, filename)

elif choice == '3':
    # Save full with timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    full_filename = f"youtube-full-history-{timestamp}.xlsx"
    save_excel(history_df, full_filename)

    # Save filtered
    start_date, end_date = get_date_range()
    filtered_df = filter_by_date(history_df.copy(), start_date, end_date)
    filtered_filename = f"youtube-history-{pd.to_datetime(start_date, dayfirst=True).strftime('%Y-%m-%d')}-to-{pd.to_datetime(end_date, dayfirst=True).strftime('%Y-%m-%d')}.xlsx"
    save_excel(filtered_df, filtered_filename)

elif choice == '4':
    start_date, end_date = get_date_range()
    filtered_df = filter_by_date(history_df.copy(), start_date, end_date)
    filename = f"youtube-ignore-filtered-{pd.to_datetime(start_date, dayfirst=True).strftime('%Y-%m-%d')}-to-{pd.to_datetime(end_date, dayfirst=True).strftime('%Y-%m-%d')}.xlsx"
    save_excel(filtered_df, filename)

else:
    print("❌ Invalid choice. Exiting.")
