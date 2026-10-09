import os
from io import BytesIO
import google.generativeai as genai
from openai import AsyncOpenAI
from telegram import Update
from telegram.ext import ContextTypes
from database import save_message, get_history

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

genai.configure(api_key=os.getenv("Ai-key"))
gemini_model = genai.GenerativeModel("gemini-2.0-flash")


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages: transcribe with Whisper, reply with Gemini."""
    voice = await update.message.voice.get_file()
    buffer = BytesIO(await voice.download_as_bytearray())
    buffer.name = "voice.ogg"

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    try:
        # 1. Transcribe with Whisper
        transcript = await client.audio.transcriptions.create(
            model="whisper-1",
            file=buffer,
            language="bn"
        )
        user_text = transcript.text
        user_id = update.effective_user.id

        await update.message.reply_text(f"📝 You said: {user_text}")

        # 2. Generate reply with Gemini
        save_message(user_id, "user", user_text)
        history = get_history(user_id)
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in history])

        response = gemini_model.generate_content(
            f"You are a Bengali-speaking friend. Reply briefly.\n\n{history_text}"
        )
        bot_reply = response.text.strip()
        save_message(user_id, "assistant", bot_reply)

        await update.message.reply_text(bot_reply)

    except Exception as e:
        print(f"Voice Error: {e}")
        await update.message.reply_text(
            "Couldn't understand the voice 😅 Send it again?"
        )
