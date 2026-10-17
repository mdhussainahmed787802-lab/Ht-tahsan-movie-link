import os
import requests
from flask import Flask, request, Response, stream_with_context

app = Flask(__name__)

BOT_TOKEN = "8466409837:AAGBFHvpuUNdIzMev8k2MuCR_1RFxw2dhWE"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
DOMAIN = "https://ht-tahsan-movie-link.onrender.com"

@app.route("/")
def home():
    return "<h1>Telegram Direct Downloader Bot is Active!</h1>"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        file_id = None

        # ভিডিও অথবা ডকুমেন্ট যেভাবেই পাঠাক ফাইল আইডি বের করবে
        if "video" in message:
            file_id = message["video"]["file_id"]
        elif "document" in message:
            file_id = message["document"]["file_id"]

        if file_id:
            download_link = f"{DOMAIN}/dl/{file_id}"
            
            requests.post(f"{TELEGRAM_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": f"✅ **আপনার ডাইরেক্ট ডাউনলোড লিংক:**\n\n🔗 {download_link}\n\nএই লিংকে চাপ দিলেই ব্রাউজারে অটো ডাউনলোড শুরু হয়ে যাবে।",
                "parse_mode": "Markdown"
            })
            
        elif "text" in message:
            requests.post(f"{TELEGRAM_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": "👋 যেকোনো ভিডিও বা ফাইল আমাকে পাঠাতেন বা ফরোয়ার্ড করুন, আমি ডাইরেক্ট লিঙ্ক বানিয়ে দেব।"
            })
            
    return "OK", 200

@app.route("/dl/<file_id>")
def direct_download(file_id):
    try:
        res = requests.get(f"{TELEGRAM_API}/getFile?file_id={file_id}").json()
        if not res.get("ok"):
            return "Error: File not found.", 400

        file_path = res["result"]["file_path"]
        download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

        req = requests.get(download_url, stream=True)
        
        def generate():
            for chunk in req.iter_content(chunk_size=8192):
                yield chunk

        return Response(
            stream_with_context(generate()),
            content_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename=file_{file_id[:6]}.mp4"}
        )
    except Exception as e:
        return f"Download Error: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
