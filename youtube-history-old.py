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

import json
import pandas as pd
from datetime import datetime

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

    import pytz
    utc = pytz.UTC

    if start_date:
        start = pd.to_datetime(start_date).replace(tzinfo=utc)
        df = df[df['time'] >= start]

    if end_date:
        end = pd.to_datetime(end_date).replace(tzinfo=utc)
        df = df[df['time'] <= end]

    # Add a column with just the date (YYYY-MM-DD)
    df['date_only'] = df['time'].dt.strftime('%Y-%m-%d')

    return df


# ==== USAGE ====
# Change the path to your downloaded file
file_path = 'watch-history.json'

# Load full history
history_df = load_youtube_history(file_path)

# 1. Extract ALL history
history_df.to_csv('youtube_full_history.csv', index=False)

# 2. Extract BETWEEN DATES
filtered_df = filter_by_date(history_df, start_date='2025-08-01', end_date='2025-08-04')
filtered_df.to_csv('youtube_filtered_history.csv', index=False)
