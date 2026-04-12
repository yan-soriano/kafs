from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("video"))
async def cmd_video(message: types.Message):
    await message.answer("Отправь мне видео, которое хочешь опубликовать.")

@router.message(lambda message: message.video)
async def handle_video(message: types.Message):
    # Логика сохранения видео и создания задачи в Celery
    await message.answer("Видео получено! Оно будет опубликовано согласно расписанию.")
