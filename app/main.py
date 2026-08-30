import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from aiogram.types import Update
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.chat import router as chat_api
from app.bot.create import create_bot, create_dispatcher
from app.config import settings
from app.llm.openrouter_client import LLMService
from app.llm.memory import ChatMemory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

memory = ChatMemory(max_messages=settings.max_history)
llm = LLMService(memory)
bot = create_bot() if settings.bot_token else None
dp = create_dispatcher() if bot else None
polling_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global polling_task
    app.state.memory = memory
    app.state.llm = llm
    app.state.bot = bot
    app.state.dp = dp

    if bot and dp:
        if settings.webhook_enabled:
            await bot.set_webhook(
                url=settings.webhook_url.rstrip("/") + settings.webhook_path,
                secret_token=settings.webhook_secret or None,
                drop_pending_updates=True,
            )
            logger.info("Telegram webhook yoqildi")
        else:
            await bot.delete_webhook(drop_pending_updates=True)
            polling_task = asyncio.create_task(
                dp.start_polling(bot, handle_signals=False)
            )
            logger.info("Telegram polling yoqildi")
    else:
        logger.warning("BOT_TOKEN yo‘q — faqat web ilova ishlaydi")

    yield

    if polling_task:
        await dp.stop_polling()
        polling_task.cancel()
        try:
            await polling_task
        except asyncio.CancelledError:
            pass
        polling_task = None

    if bot:
        if settings.webhook_enabled:
            await bot.delete_webhook()
        await bot.session.close()


app = FastAPI(title="AsadbekGPT", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(chat_api)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "model": settings.openrouter_model},
    )


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "bot": bool(bot),
        "mode": settings.bot_mode if bot else "web-only",
        "model": settings.openrouter_model,
    }


@app.post(settings.webhook_path)
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    if not bot or not dp or not settings.webhook_enabled:
        raise HTTPException(status_code=404, detail="Webhook o‘chiq")
    if settings.webhook_secret and x_telegram_bot_api_secret_token != settings.webhook_secret:
        raise HTTPException(status_code=403, detail="Secret token noto‘g‘ri")
    data = await request.json()
    update = Update.model_validate(data, context={"bot": bot})
    await dp.feed_update(bot=bot, update=update)
    return {"ok": True}
