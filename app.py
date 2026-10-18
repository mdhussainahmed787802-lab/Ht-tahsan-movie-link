import os
from pyrogram import Client, filters
from pyrogram.types import Message

BOT_TOKEN = "8466409837:AAGBFHvpuUNdIzMev8k2MoCR_1RFxw2dhWE"
API_ID = 36692904
API_HASH = "3d17643f6fa017e4449b7b5794f416fd"
DOMAIN = "https://ht-tahsan-movie-link.onrender.com"

app = Client(
    "media_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.video | filters.document | filters.audio | filters.photo)
async def media_handler(client: Client, message: Message):
    chat_id = message.chat.id
    message_id = message.id
    
    download_link = f"{DOMAIN}/dl/{chat_id}/{message_id}"
    
    await message.reply_text(
        f"✅ **আপনার ডাইরেক্ট ডাউনলোড লিংক (২ জিবি পর্যন্ত):**\n\n🔗 {download_link}\n\nএই লিংকে ক্লিক করলেই ব্রাউজারে সরাসরি ডাউনলোড শুরু হয়ে যাবে。",
        quote=True
    )

if __name__ == "__main__":
    print("Bot is running...")
    app.run()
