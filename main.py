import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from dotenv import load_dotenv
from utils.trello import add_card_to_trello
from utils.transcribe import transcribe_audio

# load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print("Warning: .env file not found at", dotenv_path)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Send me a voice note or a text message, and I’ll automatically add it to Trello.\n"
        "The bot now also evaluates audio quality and gives you an accurate result."
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    username = user.first_name or user.username or "Unknown User"
    text = update.message.text

    msg = add_card_to_trello(title=text, username=username)
    await update.message.reply_text(msg)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    username = user.first_name or user.username or "Unknown User"

    await update.message.reply_text("Converting...")

    voice = await update.message.voice.get_file()
    file_path = "voice.ogg"
    await voice.download_to_drive(file_path)

    # analyzing
    text = transcribe_audio(file_path)

    # measure audio quality
    clarity_score = evaluate_quality(text)
    clarity_msg = (
        "The audio is very clear" if clarity_score > 0.8 else
        "The audio is moderately clear." if clarity_score > 0.5 else
        "The audio is unclear or the transcription quality is poor."
    )

    #  Trello
    msg = add_card_to_trello(title=text, username=username)

    # 
    await update.message.reply_text(
        f"The audio has been successfully converted:\n\n{text}\n\n"
        f"Quality: {int(clarity_score * 100)}% - {clarity_msg}\n\n{msg}"
    )


def evaluate_quality(text: str) -> float:
    """
    Attempts to evaluate the quality of the transcribed text based on its length and apparent meaning.
    """
    if not text:
        return 0.0

    length = len(text.strip())
    word_count = len(text.split())

    #Initial evaluation based on text length
    base_score = min(length / 50, 1.0)

    #If the text is too short or contains too many symbols or dots → reduce confidence.
    penalties = 0
    if word_count < 3:
        penalties += 0.3
    if text.count(".") > 5 or "..." in text:
        penalties += 0.2
    if any(x in text for x in ["[", "]", "?", "uh", "mmm"]):
        penalties += 0.1

    final_score = max(0.0, base_score - penalties)
    return round(final_score, 2)


def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    app.run_polling()


if __name__ == "__main__":
    main()


#sudo apt-get update && sudo apt-get install ffmpeg -y
