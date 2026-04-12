import os
import httpx
import glob
from fastapi import FastAPI
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from db.models import async_session, User
from sqlalchemy import select

load_dotenv()

app = FastAPI()

CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI")


@app.get("/oauth/callback")
async def oauth_callback(code: str, state: str):
    # state — это telegram user_id который мы передали
    telegram_user_id = int(state)

    # Меняем code на access_token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://open.tiktokapis.com/v2/oauth/token/",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "client_key": CLIENT_KEY,
                "client_secret": CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": REDIRECT_URI,
            }
        )
        token_data = response.json()

    access_token = token_data.get("access_token")
    open_id = token_data.get("open_id")

    if not access_token:
        return {"error": "Не удалось получить токен"}

    # Получаем username
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            "https://open.tiktokapis.com/v2/user/info/",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"fields": "display_name,username"}
        )
        user_data = user_response.json()

    username = user_data.get("data", {}).get("user", {}).get("display_name", "")

    # Сохраняем в БД
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.id == telegram_user_id)
        )
        user = result.scalar_one_or_none()

        if user:
            user.tiktok_access_token = access_token
            user.tiktok_open_id = open_id
            user.tiktok_username = username
        else:
            user = User(
                id=telegram_user_id,
                tiktok_access_token=access_token,
                tiktok_open_id=open_id,
                tiktok_username=username,
            )
            session.add(user)

        await session.commit()

    return {"message": f"✅ TikTok аккаунт @{username} успешно подключён! Вернись в бот."}


@app.get("/tiktokK5JT9X2Yn13L9cVddSr2DDmwEET8DWGe.txt")
async def tiktok_verify():
    return FileResponse("/app/tiktokK5JT9X2Yn13L9cVddSr2DDmwEET8DWGe.txt")


@app.get("/tiktok4vWAuwBnEdeLR4ZKOocWBktNlQbcUuvN.txt")
async def tiktok_verify2():
    return FileResponse("/app/tiktok4vWAuwBnEdeLR4ZKOocWBktNlQbcUuvN.txt")


@app.get("/debug")
async def debug():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = glob.glob(f"{base_dir}/**/*tiktok*", recursive=True)
    return {"base_dir": base_dir, "files": files}


@app.get("/debug-env")
async def debug_env():
    return {
        "client_key": CLIENT_KEY,
        "redirect_uri": REDIRECT_URI
    }


@app.get("/debug-queue")
async def debug_queue():
    from db.models import Video
    async with async_session() as session:
        result = await session.execute(select(Video))
        videos = result.scalars().all()
    return [
        {
            "id": v.id,
            "scheduled_at": str(v.scheduled_at),
            "posted": v.posted,
            "user_id": v.user_id
        }
        for v in videos
    ]