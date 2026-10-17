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
    if not data:
        return "OK", 200

    # টেলিগ্রামের যেকোনো মেসেজ, এডিটেড মেসেজ বা চ্যানেল পোস্ট ক্যাচ করা
    msg = data.get("message") or data.get("edited_message") or data.get("channel_post") or data.get("edited_channel_post")
    
    if msg:
        chat_id = msg.get("chat", {}).get("id")
        file_id = None

        # ১. সরাসরি মেসেজ থেকে ফাইল আইডি খোঁজা (ভিডিও, ডকুমেন্ট, অডিও, ছবি)
        if "video" in msg:
            file_id = msg["video"]["file_id"]
        elif "document" in msg:
            file_id = msg["document"]["file_id"]
        elif "audio" in msg:
            file_id = msg["audio"]["file_id"]
        elif "photo" in msg:
            file_id = msg["photo"][-1]["file_id"]

        # ২. যদি সরাসরি না পাওয়া যায়, তবে ফরোয়ার্ড করা মেসেজ বা রিপ্লাই থেকে খোঁজা
        if not file_id:
            # ফরোয়ার্ড করা অরিজিনাল মেসেজ অবজেক্ট চেক করা
            for key in ["forward_from_message", "reply_to_message"]:
                if key in msg and isinstance(msg[key], dict):
                    sub_msg = msg[key]
                    if "video" in sub_msg:
                        file_id = sub_msg["video"]["file_id"]
                        break
                    elif "document" in sub_msg:
                        file_id = sub_msg["document"]["file_id"]
                        break
                    elif "audio" in sub_msg:
                        file_id = sub_msg["audio"]["file_id"]
                        break
                    elif "photo" in sub_msg:
                        file_id = sub_msg["photo"][-1]["file_id"]
                        break

        # ৩. যদি ফাইল আইডি পাওয়া যায়, তবে ডাইরেক্ট লিংক তৈরি করে পাঠানো
        if file_id and chat_id:
            download_link = f"{DOMAIN}/dl/{file_id}"
            
            requests.post(f"{TELEGRAM_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": f"✅ **আপনার ডাইরেক্ট ডাউনলোড লিংক:**\n\n🔗 {download_link}\n\nএই লিংকে চাপ দিলেই ব্রাউজারে অটো ডাউনলোড শুরু হয়ে যাবে।",
                "parse_mode": "Markdown"
            })
            
    return "OK", 200

@app.route("/dl/<file_id>")
def direct_download(file_id):
    try:
        res = requests.get(f"{TELEGRAM_API}/getFile?file_id={file_id}").json()
        if not res.get("ok"):
            return "Error: File not found on Telegram servers.", 400

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
