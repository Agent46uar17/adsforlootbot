from flask import Flask, jsonify, request
from flask_cors import CORS
import time, hmac, hashlib, base64

app = Flask(__name__)

# ✅ ENABLE CORS (VERY IMPORTANT)
CORS(app, origins=["https://lootbot.in"])

# 🔐 SECRET (KEEP THIS PRIVATE)
SECRET_KEY = b"YEA_BABY_FUCK_YOU"

# ⏱️ Code validity window (seconds)
WINDOW = 120  # 2 minutes


def generate_code(user_id: str):
    current_window = int(time.time()) // WINDOW
    message = f"{user_id}:{current_window}".encode()

    digest = hmac.new(
        SECRET_KEY,
        message,
        hashlib.sha256
    ).digest()

    # Short, user-friendly code
    code = base64.urlsafe_b64encode(digest[:6]).decode().rstrip("=")
    return code


@app.route("/generate", methods=["GET"])
def generate():
    user_id = request.args.get("uid")

    # 🛑 Validate input
    if not user_id or len(user_id) > 32:
        return jsonify({
            "error": "invalid uid"
        }), 400

    code = generate_code(user_id)

    return jsonify({
        "code": code,
        "expires_in": WINDOW
    })


@app.route("/")
def home():
    return "LootBot Code Generator Online", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
