import os
import httpx
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

router = Router()

CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI")


def get_tiktok_auth_url(user_id: int) -> str:
    base_url = "https://www.tiktok.com/v2/auth/authorize/"
    params = (
        f"?client_key={CLIENT_KEY}"
        f"&scope=user.info.basic,video.publish"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&state={user_id}"  # передаём telegram user_id чтобы потом связать
    )
    return base_url + params


@router.message(Command("connect"))
async def cmd_connect(message: Message):
    user_id = message.from_user.id
    auth_url = get_tiktok_auth_url(user_id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Подключить TikTok", url=auth_url)]
    ])

    await message.answer(
        "Нажми кнопку ниже чтобы подключить свой TikTok аккаунт.\n"
        "После авторизации вернись в бот.",
        reply_markup=keyboard
    )