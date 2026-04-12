from aiogram import Router, types
from aiogram.filters import Command
import os

router = Router()

@router.message(Command("tiktok"))
async def cmd_tiktok(message: types.Message):
    client_key = os.getenv("TIKTOK_CLIENT_KEY")
    redirect_uri = os.getenv("REDIRECT_URI")
    # Текст с ссылкой на OAuth
    auth_url = f"https://www.tiktok.com/auth/authorize/?client_key={client_key}&scope=video.upload&response_type=code&redirect_uri={redirect_uri}"
    
    await message.answer(f"Для подключения TikTok перейди по ссылке:\n[Авторизоваться]({auth_url})", parse_mode="Markdown")
