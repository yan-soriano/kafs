from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

app = Celery('tasks', broker=os.getenv("REDIS_URL"))

@app.task
def upload_video_to_tiktok(video_id: int):
    # Логика загрузки видео в TikTok API
    print(f"Uploading video {video_id} to TikTok...")
    return True
