import os
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
from db.models import async_session, Video

router = Router()


class VideoUpload(StatesGroup):
    waiting_for_video = State()
    waiting_for_time = State()


@router.message(Command("upload"))
async def cmd_upload(message: Message, state: FSMContext):
    await message.answer(
        "📤 Отправь мне видео которое хочешь запостить в TikTok.\n\n"
        "⚠️ Требования:\n"
        "— Формат MP4\n"
        "— Максимум 50MB\n"
    )
    await state.set_state(VideoUpload.waiting_for_video)


@router.message(VideoUpload.waiting_for_video, F.video)
async def handle_video(message: Message, state: FSMContext):
    video = message.video

    # Сохраняем file_id временно
    await state.update_data(file_id=video.file_id)

    await message.answer(
        "✅ Видео получено!\n\n"
        "📅 Теперь укажи когда его постить.\n"
        "Напиши дату и время в формате:\n"
        "ДД.ММ.ГГГГ ЧЧ:ММ\n\n"
        "Например: 25.12.2024 18:00"
    )
    await state.set_state(VideoUpload.waiting_for_time)


@router.message(VideoUpload.waiting_for_time)
async def handle_time(message: Message, state: FSMContext):
    try:
        scheduled_at = datetime.strptime(message.text, "%d.%m.%Y %H:%M")
    except ValueError:
        await message.answer(
            "❌ Неверный формат! Попробуй так:\n"
            "25.12.2024 18:00"
        )
        return

    data = await state.get_data()
    file_id = data["file_id"]

    # Сохраняем в БД
    async with async_session() as session:
        video = Video(
            user_id=message.from_user.id,
            file_url=file_id,  # пока сохраняем file_id, потом заменим на R2 URL
            scheduled_at=scheduled_at,
        )
        session.add(video)
        await session.commit()

    await state.clear()

    await message.answer(
        f"✅ Видео добавлено в очередь!\n"
        f"📅 Будет опубликовано: {scheduled_at.strftime('%d.%m.%Y в %H:%M')}"
    )


@router.message(Command("queue"))
async def cmd_queue(message: Message):
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(Video).where(
                Video.user_id == message.from_user.id,
                Video.posted == False
            )
        )
        videos = result.scalars().all()

    if not videos:
        await message.answer("📭 Очередь пуста.")
        return

    text = "📋 Твоя очередь видео:\n\n"
    for i, video in enumerate(videos, 1):
        text += f"{i}. 📅 {video.scheduled_at.strftime('%d.%m.%Y в %H:%M')}\n"

    await message.answer(text)