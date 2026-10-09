import os
import base64
from openai import AsyncOpenAI
from telegram import Update
from telegram.ext import ContextTypes

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photos using GPT-4o Vision."""
    photo_file = await update.message.photo[-1].get_file()
    image_bytes = await photo_file.download_as_bytearray()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text",
                     "text": "What is in this image? Describe it in detail in Bengali."},
                    {"type": "image_url",
                     "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }],
            max_tokens=500
        )
        reply = response.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        print(f"Image Error: {e}")
        await update.message.reply_text(
            "Couldn't understand the image 😅 Send it again?"
        )
