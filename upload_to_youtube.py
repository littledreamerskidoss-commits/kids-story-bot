import os
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_video():
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
    
    youtube = build("youtube", "v3", credentials=creds)
    
    day_num = os.environ.get("DAY_NUMBER", "1")
    content_type = os.environ.get("CONTENT_TYPE", "short")
    content_index = os.environ.get("CONTENT_INDEX", "1")
    story_lang = os.environ.get("STORY_LANG", "en").lower()
    
    file_path = f"day_{day_num}_{content_type}_{content_index}_{story_lang}.mp4"
    is_short = (content_type == "short")
    
    if is_short:
        title = f"Day {day_num} Kids Story #Shorts ({story_lang.upper()})"
    else:
        title = f"Day {day_num} Magical Adventure ({story_lang.upper()})"
    
    print(f"Preparing to upload: {file_path} as '{title}'")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: Video file not found at '{file_path}'")
    
    body = {
        "snippet": {
            "title": title,
            "description": f"Enjoy Day {day_num} magical adventure! Perfect for children ages 3-7. #KidsStories #MoralStories #KidsCartoon #{story_lang}",
            "tags": ["kids animation", "bedtime stories", "moral stories", "cartoons", story_lang],
            "categoryId": "1"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": True
        }
    }
    
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    print(f"Uploaded successfully! Video ID: {response['id']}")

if __name__ == "__main__":
    upload_video()
