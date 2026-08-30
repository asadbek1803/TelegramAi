from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from app.config import settings

OPEN_APP_BTN = "Ilovani ochish"


def webapp_text(intro: str | None = None) -> str:
    lead = intro or (
        "Salom! Men <b>AsadbekGPT</b> — sizning AI yordamchingizman."
    )
    return (
        f"{lead}\n\n"
        "Suhbat faqat web ilovada. Pastdagi tugmani bosing."
    )


def webapp_keyboard() -> InlineKeyboardMarkup | None:
    if not settings.webapp_is_https:
        return None
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=OPEN_APP_BTN,
                    web_app=WebAppInfo(url=settings.webapp_url),
                )
            ]
        ]
    )
