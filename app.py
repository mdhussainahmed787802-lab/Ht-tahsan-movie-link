import os
import asyncio
from flask import Flask, request, Response, stream_with_context
from pyrogram import Client

BOT_TOKEN = "8466409837:AAGBFHvpuUNdIzMev8k2MoCR_1RFxw2dhWE"
API_ID = 36692904
API_HASH = "3d17643f6fa017e4449b7b5794f416fd"
# রেলওয়ে প্রজেক্ট লাইভ হওয়ার পর যে লিংক পাবেন, সেটি এখানে বসাবেন (যেমন: https://xxx.railway.app)
DOMAIN = "https://your-railway-app-url.railway.app"

app = Flask(__name__)

def get_or_create_event_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

@app.route("/")
def home():
    return "<h1>Railway Pyrogram Telegram Direct Downloader is Active!</h1>"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if data:
        async def handle_update():
            async with Client("bot_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True) as bot:
                try:
                    msg_data = data.get("message") or data.get("edited_message") or data.get("channel_post") or data.get("edited_channel_post")
                    if msg_data:
                        chat_id = msg_data.get("chat", {}).get("id")
                        message_id = msg_data.get("message_id")
                        
                        if chat_id and message_id:
                            msg = await bot.get_messages(chat_id, message_id)
                            if msg and (msg.video or msg.document or msg.audio or msg.photo):
                                # ফাইলের আসল নাম বা ক্যাপশন বের করা যাতে লিঙ্কে সুন্দর নাম আসে
                                file_name = "video.mp4"
                                if msg.video and msg.video.file_name:
                                    file_name = msg.video.file_name
                                elif msg.document and msg.document.file_name:
                                    file_name = msg.document.file_name
                                elif msg.caption:
                                    file_name = msg.caption[:30].strip() + ".mp4"
                                
                                download_link = f"{DOMAIN}/dl/{chat_id}/{message_id}/{file_name}"
                                await bot.send_message(
                                    chat_id,
                                    f"✅ **আপনার ডাইরেক্ট ডাউনলোড লিংক (২ জিবি পর্যন্ত):**\n\n🔗 {download_link}\n\nএই লিংকে ক্লিক করলেই ব্রাউজারে সরাসরি ডাউনলোড শুরু হয়ে যাবে।"
                                )
                except Exception as e:
                    print(f"Webhook error: {e}")

        loop = get_or_create_event_loop()
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(handle_update(), loop)
        else:
            loop.run_until_complete(handle_update())
            
    return "OK", 200

@app.route("/dl/<int:chat_id>/<int:message_id>", defaults={"file_name": "video.mp4"})
@app.route("/dl/<int:chat_id>/<int:message_id>/<path:file_name>")
def direct_download(chat_id, message_id, file_name):
    async def stream_file():
        async with Client("stream_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True) as stream_app:
            msg = await stream_app.get_messages(chat_id, message_id)
            if not msg or not (msg.video or msg.document or msg.audio or msg.photo):
                return
            async for chunk in stream_app.stream_media(msg):
                yield chunk

    def generate():
        loop = get_or_create_event_loop()
        generator = stream_file()
        while True:
            try:
                if loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(generator.__anext__(), loop)
                    chunk = future.result()
                else:
                    chunk = loop.run_until_complete(generator.__anext__())
                yield chunk
            except (StopAsyncIteration, StopIteration):
                break
            except Exception as e:
                print(f"Stream error: {e}")
                break

    return Response(
        stream_with_context(generate()),
        content_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
