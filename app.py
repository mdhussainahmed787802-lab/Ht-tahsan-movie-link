import os
import asyncio
from flask import Flask, request, Response, stream_with_context
from pyrogram import Client
from pyrogram.types import Message

BOT_TOKEN = "8466409837:AAGBFHvpuUNdIzMev8k2MuCR_1RFxw2dhWE"
API_ID = 36692904
API_HASH = "3d17643f6fa017e4449b7b5794f416fd"
DOMAIN = "https://ht-tahsan-movie-link.onrender.com"

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Telegram Large File Direct Downloader is Active!</h1>"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if data:
        async def process_update():
            async with Client("bot_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN) as bot:
                try:
                    update = bot.dispatcher.parse_update(data)
                    if update and isinstance(update, Message):
                        msg = update
                        media = msg.video or msg.document or msg.audio or (msg.photo[-1] if msg.photo else None)
                        if media:
                            download_link = f"{DOMAIN}/dl/{msg.chat.id}/{msg.id}"
                            await bot.send_message(
                                msg.chat.id,
                                f"✅ **আপনার ডাইরেক্ট ডাউনলোড লিংক:**\n\n🔗 {download_link}\n\nএই লিংকে ক্লিক করলেই ব্রাউজারে অটো ডাউনলোড শুরু হয়ে যাবে।"
                            )
                except Exception as e:
                    print(f"Error handling update: {e}")

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        loop.run_until_complete(process_update())

    return "OK", 200

@app.route("/dl/<int:chat_id>/<int:message_id>")
def direct_download(chat_id, message_id):
    async def stream_file():
        async with Client("stream_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN) as stream_app:
            msg = await stream_app.get_messages(chat_id, message_id)
            if not msg or not (msg.video or msg.document or msg.audio or msg.photo):
                return
            async for chunk in stream_app.stream_media(msg):
                yield chunk

    def generate():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            generator = stream_file()
            while True:
                try:
                    chunk = loop.run_until_complete(generator.__anext__())
                    yield chunk
                except StopAsyncIteration:
                    break
        finally:
            loop.close()

    return Response(
        stream_with_context(generate()),
        content_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename=file_{message_id}.mp4"}
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
