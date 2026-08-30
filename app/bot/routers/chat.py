from aiogram import F, Router
from aiogram.types import Message

from app.bot.prompts import webapp_keyboard, webapp_text

router = Router(name="chat")


@router.message(F.text)
async def block_text(message: Message) -> None:
    await message.answer(
        webapp_text("Bu yerda yozib bo‘lmaydi — suhbat faqat ilovada."),
        reply_markup=webapp_keyboard(),
    )
