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
        privacy_options = creator_data.get("data", {}).get("privacy_level_options", ["SELF_ONLY"])
        privacy_level = "PUBLIC_TO_EVERYONE" if "PUBLIC_TO_EVERYONE" in privacy_options else privacy_options[0]

        # Шаг 2 — инициируем постинг
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
                    "source": "PULL_FROM_URL",
                    "video_url": video.file_url
                }
            }
        )
        post_data = post_response.json()

    if post_data.get("error", {}).get("code") == "ok":
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
    else:
        print(f"❌ Ошибка постинга видео {video_id}: {post_data}")


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