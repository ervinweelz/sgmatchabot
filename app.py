import os
from flask import Flask, request
import requests

TOKEN = os.environ.get("TELEGRAM_TOKEN")

app = Flask(__name__)

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        if text.lower() == "/start":
            send_message(chat_id, "Hello! Welcome to your Flask bot on Render.")
        else:
            send_message(chat_id, f"You said: {text}")
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

#https://api.telegram.org/bot7971717836:AAEg-0paQG3qBzbYOfvnpkY4DQHRk6YAj00/setWebhook?url=https://sgmatchabot.onrender.com/webhook/7971717836:AAEg-0paQG3qBzbYOfvnpkY4DQHRk6YAj00
