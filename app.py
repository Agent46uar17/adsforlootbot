from flask import Flask, jsonify, request
from flask_cors import CORS
import hmac, hashlib, base64
from datetime import datetime
from zoneinfo import ZoneInfo

app = Flask(__name__)

# ✅ ENABLE CORS
CORS(app, origins=["https://lootbot.in"])

# 🔐 SECRET (KEEP THIS PRIVATE)
SECRET_KEY = b"lolbrolol"

# ⏱️ Code validity window (seconds)
WINDOW = 120  # 2 minutes


def generate_code(user_id: str):
    # 🕒 CET / CEST time (auto DST)
    cet_now = datetime.now(ZoneInfo("Europe/Berlin"))

    # unix timestamp based on CET
    timestamp = int(cet_now.timestamp())

    current_window = timestamp // WINDOW
    message = f"{user_id}:{current_window}".encode()

    digest = hmac.new(
        SECRET_KEY,
        message,
        hashlib.sha256
    ).digest()

    # short, user-friendly code
    code = base64.urlsafe_b64encode(digest[:6]).decode().rstrip("=")
    return code


@app.route("/generate", methods=["GET"])
def generate():
    user_id = request.args.get("uid")

    # 🛑 Validate input
    if not user_id or len(user_id) > 32:
        return jsonify({"error": "invalid uid"}), 400

    code = generate_code(user_id)

    return jsonify({
        "code": code,
        "expires_in": WINDOW,
        "timezone": "CET / CEST"
    })


@app.route("/")
def home():
    return "LootBot Code Generator Online (CET)", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
