import os
import json
import google.oauth2.credentials
from googleapiclient.discovery import build

def analyze_channel_performance():
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")
    
    creds = google.oauth2.credentials.Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret
    )
    
    youtube_analytics = build("youtubeAnalytics", "v2", credentials=creds)
    
    try:
        response = youtube_analytics.reports().query(
            ids="channel==MINE",
            startDate="2026-01-01",
            endDate="2026-12-31",
            metrics="views,averageViewDuration",
            dimensions="video",
            sort="-views",
            maxResults=5
        ).execute()
        print("Analytics fetched successfully:", response)
    except Exception as e:
        print("Analytics check skipped or no data yet:", e)
    
    # Self-update channel memory file for future story generation
    memory_data = {"preferred_theme": "magical forest and space adventures", "boost_factor": 1.5}
    with open("channel_memory.json", "w") as f:
        json.dump(memory_data, f)
    print("Channel memory updated automatically.")

if __name__ == "__main__":
    analyze_channel_performance()
