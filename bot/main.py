import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot.handlers import start, tiktok, video
from dotenv import load_dotenv
import os

load_dotenv()

async def main():
    logging.basicConfig(level=logging.INFO)
    
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()

    # Register routers
    dp.include_router(start.router)
    dp.include_router(tiktok.router)
    dp.include_router(video.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
