import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

SITE_ORIGIN = "https://lakhoa25103200014-ui.github.io"
EXPECTED_HOSTNAME = "lakhoa25103200014-ui.github.io"

CORS(app, resources={
    r"/verify": {"origins": [SITE_ORIGIN]}
})


@app.get("/")
def health():
    return jsonify(status="running")


@app.post("/verify")
def verify():
    data = request.get_json(silent=True) or {}
    token = data.get("token")

    if not isinstance(token, str) or not token or len(token) > 8192:
        return jsonify(success=False), 400

    secret = os.environ.get("TURNSTILE_SECRET_KEY")
    if not secret:
        app.logger.error("Missing Turnstile secret")
        return jsonify(success=False), 500

    try:
        response = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={"secret": secret, "response": token},
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()

        valid = (
            result.get("success") is True
            and result.get("hostname") == EXPECTED_HOSTNAME
        )
        return jsonify(success=valid)

    except (requests.RequestException, ValueError):
        app.logger.exception("Turnstile request failed")
        return jsonify(success=False), 502
