import os
import logging
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ==========================
# Логування
# ==========================
LOG_FILE = "bot.log"
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# ==========================
# Налаштування
# ==========================
BOT_TOKEN = "7753936376:AAHUuZZe1vZF8frLcAizPyCWmrSkimh2St4"       # Встав свій токен від BotFather
ADMIN_CHAT_ID = 8322279458          # Твій Telegram ID
MEDIA_DIR = "received_media"
os.makedirs(MEDIA_DIR, exist_ok=True)

# ==========================
# Команда /start
# ==========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Вітаю! Це анонімний бот 'Хортицька Варта'. Надсилай текст, фото або відео."
    )

# ==========================
# Обробка тексту
# ==========================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    await update.message.reply_text("Ваше повідомлення отримано ✅")
    
    # Пересилка адміністратору
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"[Текст] Від користувача {user_id}:\n{text}"
    )
    logging.info(f"Текст від {user_id}: {text}")

# ==========================
# Обробка фото
# ==========================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_path = os.path.join(MEDIA_DIR, f"{file.file_id}.jpg")
    await file.download_to_drive(file_path)
    await update.message.reply_text("Фото отримано ✅")
    
    with open(file_path, "rb") as f:
        await context.bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=f,
            caption=f"Фото від користувача {user_id}\nФайл: {file.file_id}.jpg"
        )
    logging.info(f"Фото від {user_id}: {file.file_id}.jpg")

# ==========================
# Обробка відео
# ==========================
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    video = update.message.video
    file = await video.get_file()
    file_path = os.path.join(MEDIA_DIR, f"{file.file_id}.mp4")
    await file.download_to_drive(file_path)
    await update.message.reply_text("Відео отримано ✅")
    
    with open(file_path, "rb") as f:
        await context.bot.send_video(
            chat_id=ADMIN_CHAT_ID,
            video=f,
            caption=f"Відео від користувача {user_id}\nФайл: {file.file_id}.mp4"
        )
    logging.info(f"Відео від {user_id}: {file.file_id}.mp4")

# ==========================
# Обробка помилок
# ==========================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error(msg="Помилка виклику оновлення:", exc_info=context.error)
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"⚠️ Сталася помилка:\n{context.error}"
    )

# ==========================
# Основна функція
# ==========================
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_error_handler(error_handler)

    logging.info("Бот 'Хортицька Варта' запущено...")
    app.run_polling()
