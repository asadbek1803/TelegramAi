from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.prompts import webapp_keyboard, webapp_text

router = Router(name="help")


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(webapp_text(), reply_markup=webapp_keyboard())


@router.message(Command("new"))
async def cmd_new(message: Message) -> None:
    await message.answer(
        webapp_text(
            "Yangi suhbat uchun ilovani oching va <b>+</b> tugmasini bosing."
        ),
        reply_markup=webapp_keyboard(),
    )
