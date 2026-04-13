import os
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from sqlalchemy import select
from db.models import async_session, Video, User

scheduler = AsyncIOScheduler()


async def post_video(video_id: int):
    async with async_session() as session:
        # Получаем видео
        video_result = await session.execute(
            select(Video).where(Video.id == video_id)
        )
        video = video_result.scalar_one_or_none()

        if not video or video.posted:
            return

        # Получаем токен пользователя
        user_result = await session.execute(
            select(User).where(User.id == video.user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user or not user.tiktok_access_token:
            print(f"❌ Нет токена для пользователя {video.user_id}")
            return

    # Скачиваем файл из Telegram по file_id
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    async with httpx.AsyncClient() as client:
        # Получаем file_path
        file_info = await client.get(
            f"https://api.telegram.org/bot{bot_token}/getFile",
            params={"file_id": video.file_url}
        )
        file_data = file_info.json()
        print(f"📁 File info: {file_data}")

        if not file_data.get("ok"):
            print(f"❌ Telegram не нашёл файл: {file_data}")
            return

        file_path = file_data["result"]["file_path"]
        
        # Скачиваем файл
        file_response = await client.get(
            f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
        )
        video_bytes = file_response.content
        video_size = len(video_bytes)

    async with httpx.AsyncClient() as client:
        # Шаг 1 — получаем инфо о креаторе
        creator_response = await client.post(
            "https://open.tiktokapis.com/v2/post/publish/creator_info/query/",
            headers={
                "Authorization": f"Bearer {user.tiktok_access_token}",
                "Content-Type": "application/json; charset=UTF-8"
            }
        )
        creator_data = creator_response.json()
        print(f"👤 Creator info: {creator_data}")
        # Принудительно ставим SELF_ONLY пока приложение не прошло аудит
        privacy_level = "SELF_ONLY"

        # Шаг 2 — инициируем FILE_UPLOAD
        post_response = await client.post(
            "https://open.tiktokapis.com/v2/post/publish/video/init/",
            headers={
                "Authorization": f"Bearer {user.tiktok_access_token}",
                "Content-Type": "application/json; charset=UTF-8"
            },
            json={
                "post_info": {
                    "title": video.description or "Check this out! 🔥",
                    "privacy_level": privacy_level,
                    "disable_duet": False,
                    "disable_comment": False,
                    "disable_stitch": False,
                },
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_size": video_size,
                    "chunk_size": video_size,
                    "total_chunk_count": 1
                }
            }
        )
        post_data = post_response.json()
        print(f"📝 Init response: {post_data}")

        if post_data.get("error", {}).get("code") != "ok":
            print(f"❌ Ошибка init: {post_data}")
            return

        upload_url = post_data["data"]["upload_url"]

        # Шаг 3 — загружаем файл
        upload_response = await client.put(
            upload_url,
            headers={
                "Content-Range": f"bytes 0-{video_size-1}/{video_size}",
                "Content-Type": "video/mp4"
            },
            content=video_bytes
        )
        print(f"📤 Upload response: {upload_response.status_code}")

    # Помечаем как опубликованное
    async with async_session() as session:
        result = await session.execute(
            select(Video).where(Video.id == video_id)
        )
        video = result.scalar_one_or_none()
        if video:
            video.posted = True
            await session.commit()
    print(f"✅ Видео {video_id} опубликовано!")


async def check_scheduled_videos():
    """Проверяем каждую минуту — не пора ли постить"""
    now = datetime.utcnow()
    print(f"🕐 Проверка очереди: {now}")

    async with async_session() as session:
        result = await session.execute(
            select(Video).where(
                Video.posted == False,
                Video.scheduled_at <= now
            )
        )
        videos = result.scalars().all()

    print(f"📋 Найдено видео для постинга: {len(videos)}")

    for video in videos:
        print(f"📤 Постим видео {video.id}...")
        await post_video(video.id)


def start_scheduler():
    scheduler.add_job(check_scheduled_videos, "interval", minutes=1)
    scheduler.start()
    print("✅ Планировщик запущен!")