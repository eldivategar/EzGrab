import os

storage_dir = "storage"

def youtube_storage_dir(video_id: str) -> str:
    os.makedirs(os.path.join(storage_dir, "youtube", video_id), exist_ok=True)
    return os.path.join(storage_dir, "youtube", video_id)