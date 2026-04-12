from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Я помогу тебе автоматически постить видео в TikTok.\n\n"
        "Что я умею:\n"
        "📱 /connect — подключить TikTok аккаунт\n"
        "📤 /upload — загрузить видео\n"
        "📅 /queue — посмотреть очередь видео\n\n"
        "Начни с /connect чтобы подключить свой TikTok!"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📖 Как пользоваться:\n\n"
        "1. /connect — подключи TikTok аккаунт\n"
        "2. Отправь видео в чат\n"
        "3. Укажи время когда постить\n"
        "4. Всё — бот сам опубликует!\n"
    )