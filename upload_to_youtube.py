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
    
    is_short = os.environ.get("VIDEO_TYPE") == "short"
    file_path = "final_short.mp4" if is_short else "final_video.mp4"
    title = "Bedtime Story for Kids - Animated Adventure #Shorts" if is_short else "Magical Bedtime Story for Kids | Moral Animated Tale"
    
    body = {
        "snippet": {
            "title": title,
            "description": "Enjoy this wonderful animated story for kids, created automatically!",
            "tags": ["kids animation", "bedtime stories", "moral stories", "cartoons"],
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
