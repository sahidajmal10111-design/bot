import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import ContextTypes
from database import save_message, get_history, update_profile, get_profile

genai.configure(api_key=os.getenv("Ai-key"))
model = genai.GenerativeModel("gemini-2.0-flash")

# System prompt (bot's personality)
SYSTEM_PROMPT = """You are a friendly, empathetic Bengali-speaking friend.
Rules:
- Speak in natural, casual Bengali (use "তুমি", not "আপনি")
- Keep replies short, like texting a friend on WhatsApp
- Use emojis occasionally, not too many
- Never sound robotic or like a book
- Understand the user's mood and respond accordingly
- If someone is sad, be empathetic; if happy, share the joy
- Make light jokes when appropriate
- Never say you are an AI; talk like a real human
- Remember the user's name and preferences"""


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages."""
    user_id = update.effective_user.id
    user_message = update.message.text

    # Extract name if user says "আমার নাম ..."
    if "আমার নাম" in user_message:
        try:
            name = user_message.split("আমার নাম")[-1].strip().split()[0]
            update_profile(user_id, name=name)
            await update.message.reply_text(f"Alright {name}, I'll remember that! 😊")
            return
        except Exception:
            pass

    save_message(user_id, "user", user_message)

    history = get_history(user_id)
    profile = get_profile(user_id)

    profile_info = ""
    if profile["name"]:
        profile_info += f"\nUser's name: {profile['name']}"
    if profile["preferences"]:
        profile_info += f"\nUser's preferences: {profile['preferences']}"

    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in history])

    full_prompt = f"""{SYSTEM_PROMPT}{profile_info}

Previous conversation:
{history_text}

Now reply to the user's latest message:"""

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    try:
        response = model.generate_content(full_prompt)
        bot_reply = response.text.strip()
        save_message(user_id, "assistant", bot_reply)
        await update.message.reply_text(bot_reply)
    except Exception as e:
        print(f"Gemini Error: {e}")
        await update.message.reply_text("Oops! Something went wrong 😅 Say that again?")
