import src.core.env as env

import os
import random

from zoneinfo import ZoneInfo # WIB : Asia/Jakarta, WITA : Asia/Makassar, WIT : Asia/Jayapura

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import (
    ContextTypes,
    Application,
    CommandHandler, # /start, /report
    MessageHandler, # text atau suara (voice note)
    Defaults,
    filters
)

from telegram.constants import ParseMode # MarkdownV2
from loguru import logger
from datetime import time, date, timedelta, datetime # Generate - per 1 minggu / 7 hari

from src.agents.lead import LeadAgent
from src.repository.chat_repository import ChatRepository
from src.core.format import to_telegram_markdown
from src.core.artifacts import Artifact

timezone = ZoneInfo("Asia/Jayapura") # WIT
hoursnow = int(datetime.now(timezone).strftime("%H"))

chat_repository = ChatRepository()
lead_agent = LeadAgent()

# python-telegram-bot-config
bot_config = Defaults(parse_mode=ParseMode.MARKDOWN_V2, tzinfo=timezone)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    chat_id = update.effective_chat.id

    chat_repository.save_user(user_id=user_id, username=username, chat_id=chat_id)

    safe_text = to_telegram_markdown(
        f"Halo! Selamat datang {username} di Mentor Bahasa Inggris Virtual.\n"
        "Aku siap bantu kamu untuk belajar Bahasa Inggris! \n"
        "Kamu bisa langsung coba ketik pesan seperti ini: \n"
        "- *buatkan soal reading*\n"
        "- *periksa: I goes to school*\n"
        "- *kasih tips belajar*\n"
        "atau ngobrol bebas untuk melatih *speaking atau writing* kamu!\n"
        "- Ketik /start untuk mendaftarkan akun dan mulai belajar\n"
        "- Ketik /report untuk membuat laporan belajar\n",
    )

    await update.message.reply_text(safe_text)

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        to_telegram_markdown("Laporan sedang kami buat, mohon tunggu...")
    )

    user_id = update.message.from_user.id
    username = update.message.from_user.username

    end_date = date.today()
    start_date = end_date - timedelta(days=7)

    report_file_path = lead_agent.handle_report(user_id=user_id, username=username, start_date=start_date, end_date=end_date)

    with open(report_file_path, "rb") as report_pdf:
        await update.message.reply_document(
            document=report_pdf,
            caption=to_telegram_markdown(
                f"Laporan belajar Bahasa Inggris dari tanggal {start_date.isoformat()} - {end_date.isoformat()}"
            ),
        )

    os.remove(report_file_path)

async def _send_artifact(update: Update, artifact: Artifact):
    artifact_path = artifact.get("path")
    kind = artifact.get("kind")
    caption = artifact.get("caption")

    safe_caption_text = to_telegram_markdown(caption)

    if not os.path.exists(artifact_path):
        logger.warning(f"Artifact tidak ditemukan")

    with open(artifact_path, "rb") as artifact_file:
        if kind == "audio":
            await update.message.reply_audio(
                audio=artifact_file,
                caption=safe_caption_text
            )
        else:
            await update.message.reply_document(
                document=artifact_file,
                caption=safe_caption_text
            )

    os.remove(artifact_path)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_text = await update.message.reply_text(
        to_telegram_markdown("Mentor sedang menyiapkan jawaban...")
    )

    user_id = update.message.from_user.id
    user_message = update.message.text

    response = lead_agent.handle_send_message(
        user_id=user_id, message_text=user_message
    )

    safe_text = to_telegram_markdown(response["text"])

    await reply_text.edit_text(safe_text)

    if response["artifacts"]:
        artifact = Artifact(response["artifacts"][0])
        await _send_artifact(update, artifact)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_text = await update.message.reply_text(
        to_telegram_markdown("Suara sedang kami proses, mohon tunggu...")
    )

    user_id = update.message.from_user.id

    env.TEMP.mkdir(parents=True, exist_ok=True)
    voice_file = await context.bot.get_file(update.message.voice.file_id)
    voice_file_path = env.TEMP/f"{update.message.voice.file_id}.ogg"
    await voice_file.download_to_drive(str(voice_file_path))

    evaluation_speaking_result = lead_agent.handle_send_voice(
        user_id=user_id,
        voice_file_path=voice_file_path
    )

    safe_text = to_telegram_markdown(evaluation_speaking_result)

    await reply_text.edit_text(safe_text)

    os.remove(str(voice_file_path))

async def task_reminder(context: ContextTypes.DEFAULT_TYPE):
    users = chat_repository.get_users()
    skill_types = ["reading", "writing", "listening", "speaking"]

    logger.info(f"Saat ini pukul {hoursnow} WIT")
    for user in users.data:
        user_id = user["user_id"]
        username = user["username"]
        get_reminder = user["get_reminder"]
        
        sapaan_waktu = "" # Backup jika sistem mendetaksi di luar if
        if hoursnow <= 10:
            sapaan_waktu = f"Selamat pagi, {username}! ☀️"
        elif 10 < hoursnow < 15:
            sapaan_waktu = f"Selamat siang, {username}! ☀️"
        elif 15 <= hoursnow < 18:
            sapaan_waktu = f"Selamat sore, {username}!"
        elif hoursnow >= 18:
            sapaan_waktu = f"Selamat malam, {username}!"

        message = f"{sapaan_waktu} Yuk, luangkan 5 menit untuk latihan {random.choice(skill_types)} hari ini."

        if get_reminder == True:
            logger.info(message)
            chat_repository.save_message(
                user_id=user_id,
                role="model",
                message_text=message
            )
            safe_text = to_telegram_markdown(message)
            await context.bot.send_message(chat_id=user_id, text=safe_text)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")

    if update.effective_message:
        await update.effective_message.reply_text(f"Terjadi error: {context.error}")

def run():
    app = (
        Application.builder().token(env.TELEGRAM_BOT_TOKEN).defaults(bot_config).build()
    )

    # Register route handler
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("report", report_command))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    # Fitur reminder
    target_time = time(hour=19, minute=6, second=0, tzinfo=timezone)
    app.job_queue.run_daily(callback=task_reminder, time=target_time, name="task_reminder")
    # app.job_queue.run_repeating(callback=task_reminder, interval=5, first=0)

    app.add_error_handler(error_handler)

    print("Mentor Bahasa Inggris Virtual berhasil dijalankan...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, timeout=30)
