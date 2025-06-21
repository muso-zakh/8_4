import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN
from database import init_db
from custom_command import set_commands
from general import basic_router
from catalog import catalog_router

async def main():
    init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    await set_commands(bot)

    dp = Dispatcher()
    dp.include_routers(basic_router, catalog_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
