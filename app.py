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


def get_current_window():
    """Get current CET/CEST window"""
    cet_now = datetime.now(ZoneInfo("Europe/Berlin"))
    timestamp = int(cet_now.timestamp())
    return timestamp // WINDOW


def generate_code(user_id: str, window: int):
    message = f"{user_id}:{window}".encode()

    digest = hmac.new(
        SECRET_KEY,
        message,
        hashlib.sha256
    ).digest()

    return base64.urlsafe_b64encode(digest[:6]).decode().rstrip("=")


# 🔹 GENERATE CODE
@app.route("/generate", methods=["GET"])
def generate():
    user_id = request.args.get("uid")

    if not user_id or len(user_id) > 32:
        return jsonify({"error": "invalid uid"}), 400

    window = get_current_window()
    code = generate_code(user_id, window)

    return jsonify({
        "uid": user_id,
        "code": code,
        "expires_in": WINDOW,
        "window": window,
        "timezone": "CET / CEST"
    })


# 🔹 DECODE / VERIFY CODE
@app.route("/decode", methods=["GET"])
def decode():
    user_id = request.args.get("uid")
    provided_code = request.args.get("code")

    if not user_id or not provided_code:
        return jsonify({"error": "uid and code required"}), 400

    current_window = get_current_window()

    # allow small tolerance
    for offset in (0, -1, 1):
        test_window = current_window + offset
        expected_code = generate_code(user_id, test_window)

        if hmac.compare_digest(expected_code, provided_code):
            return jsonify({
                "valid": True,
                "uid": user_id,
                "window": test_window,
                "timezone": "CET / CEST"
            })

    return jsonify({
        "valid": False,
        "reason": "invalid or expired code"
    }), 400


@app.route("/")
def home():
    return "LootBot Code Generator + Decoder (CET)", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
