from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.routers.chat import router as chat_router
from app.bot.routers.help import router as help_router
from app.bot.routers.start import router as start_router
from app.config import settings


def create_bot() -> Bot:
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(start_router)
    dp.include_router(help_router)
    dp.include_router(chat_router)
    return dp
