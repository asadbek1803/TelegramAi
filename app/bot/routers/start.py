from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.prompts import webapp_keyboard, webapp_text

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(webapp_text(), reply_markup=webapp_keyboard())
