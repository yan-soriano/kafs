from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот для автопостинга в TikTok.\nИспользуй /help для списка команд.")

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("Команды:\n/start - Начать работу\n/tiktok - Подключить аккаунт TikTok\n/video - Загрузить видео")
