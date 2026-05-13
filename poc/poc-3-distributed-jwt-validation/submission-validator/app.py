"""
Submission Validator Service - HackLab POC 3

Valideert ingediende flags. Doet zelfstandige JWT-validatie met de
public key (ADR 005: gedistribueerde validatie).

Bewijst samen met challenge-catalog dat MEERDERE services onafhankelijk
kunnen valideren zonder coordinatie met User Management.
"""

import jwt
from flask import Flask, jsonify, request

PUBLIC_KEY_PATH = "/run/secrets/jwt_public_key"

with open(PUBLIC_KEY_PATH, "rb") as f:
    PUBLIC_KEY = f.read()

CORRECT_FLAGS = {
    1: "FLAG{sql_injection_basics}",
    2: "FLAG{xss_reflected}",
    3: "FLAG{buffer_overflow}",
}

app = Flask(__name__)


def validate_token():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None, (jsonify({"error": "Ontbrekend of foutief token"}), 401)

    token = auth[7:]
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, (jsonify({"error": "Token verlopen"}), 401)
    except jwt.InvalidTokenError as e:
        return None, (jsonify({"error": f"Ongeldig token: {e}"}), 401)


@app.route("/submit", methods=["POST"])
def submit():
    payload, err = validate_token()
    if err:
        return err

    data = request.get_json(silent=True) or {}
    challenge_id = data.get("challenge_id")
    flag = data.get("flag")

    if challenge_id is None or flag is None:
        return jsonify({"error": "challenge_id en flag zijn verplicht"}), 400

    correct = CORRECT_FLAGS.get(challenge_id) == flag
    return jsonify(
        {
            "user": payload["sub"],
            "challenge_id": challenge_id,
            "correct": correct,
        }
    )


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"service": "submission-validator", "status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
