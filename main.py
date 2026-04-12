import asyncio
import os
import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from db.models import init_db
from bot.handlers import start, tiktok, video
from scheduler.tasks import start_scheduler
from api.main import app as fastapi_app

load_dotenv()

bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher(storage=MemoryStorage())


async def main():
    # Инициализируем БД
    await init_db()

    # Подключаем хэндлеры
    dp.include_router(start.router)
    dp.include_router(tiktok.router)
    dp.include_router(video.router)

    # Запускаем планировщик
    start_scheduler()

    # Запускаем FastAPI в фоне
    config = uvicorn.Config(
        fastapi_app, 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8000))
    )
    server = uvicorn.Server(config)
    
    # Запускаем бота и сервер одновременно
    await asyncio.gather(
        dp.start_polling(bot),
        server.serve()
    )


if __name__ == "__main__":
    asyncio.run(main())