# AsadbekGPT

OpenRouter (bepul modellar) asosidagi AI chat. O‘zini **AsadbekGPT** deb tanishtiradi.

- **Web ilova** — telefon shaklidagi ChatGPT uslubidagi interfeys (`http://127.0.0.1:8000`)
- **Telegram bot** — faqat Web App ochish (`/start`, `/help`, `/new`); matnli chat yo‘q

Ikkala kanal ham bitta OpenRouter servisini chaqiradi. API kalit faqat serverda turadi.

## Talablar

- Python 3.11+
- [OpenRouter API kaliti](https://openrouter.ai/keys) (bepul modellar mavjud)
- Telegram bot tokeni ([BotFather](https://t.me/BotFather)) — ixtiyoriy, faqat bot uchun

## Ishga tushirish (Windows)

```powershell
cd C:\Users\asadb\Desktop\AsadbekChatBot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

`.env` ni ochib yozing:

```
OPENROUTER_API_KEY=sk-or-...
BOT_TOKEN=123456:ABC...
OPENROUTER_MODEL=openrouter/free
BOT_MODE=polling
WEBAPP_URL=http://127.0.0.1:8000
```

Keyin:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Brauzerda oching: http://127.0.0.1:8000

`BOT_TOKEN` bo‘lsa, Telegram polling avtomatik yoqiladi. Bo‘lmasa faqat web ishlaydi.

## Telegram Web App tugmasi

Mini App tugmasi faqat `WEBAPP_URL` `https://` bilan boshlansa chiqadi (Telegram talabi). Lokalda `http://127.0.0.1:8000` ni brauzerda oching. Productionda HTTPS domen qo‘ying va BotFather da domain belgilang.

## Production webhook

```
BOT_MODE=webhook
WEBHOOK_URL=https://your-domain.com
WEBHOOK_SECRET=uzun-maxfiy-soz
WEBAPP_URL=https://your-domain.com
```

## Telegram buyruqlari

Botda yozib bo‘lmaydi — faqat web ilova orqali suhbat. Barcha buyruqlar ilovani ochish uchun:

| Buyruq | Vazifa |
|---|---|
| `/start` | Ilovani ochish |
| `/help` | Ilovani ochish |
| `/new` | Ilovada yangi suhbat haqida eslatma |
