from flask import Flask, jsonify, request
import time, hmac, hashlib, base64

app = Flask(__name__)

SECRET_KEY = b"SUPER_SECRET_CHANGE_THIS_123"
WINDOW = 120  # 2 minutes

def generate_code(user_id: str):
    current_window = int(time.time()) // WINDOW
    message = f"{user_id}:{current_window}".encode()

    digest = hmac.new(SECRET_KEY, message, hashlib.sha256).digest()
    code = base64.urlsafe_b64encode(digest[:6]).decode().rstrip("=")

    return code

@app.route("/generate")
def generate():
    user_id = request.args.get("uid")
    if not user_id:
        return jsonify({"error": "missing uid"}), 400

    code = generate_code(user_id)
    return jsonify({
        "code": code,
        "expires_in": WINDOW
    })

@app.route("/")
def home():
    return "LootBot Code Generator Online"
