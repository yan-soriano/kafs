from fastapi import FastAPI, Request
import os

app = FastAPI()

@app.get("/callback")
async def tiktok_callback(code: str, state: str = None):
    # Логика обмена code на access_token
    # И обновление данных пользователя в БД
    return {"status": "success", "message": "TikTok account connected! You can return to the bot."}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
