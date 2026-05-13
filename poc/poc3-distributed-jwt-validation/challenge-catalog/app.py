"""
Challenge Catalog Service - HackLab POC 3

Beheert de lijst van beschikbare challenges. Valideert JWT-tokens
ZELFSTANDIG met de public key, zonder de User Management service
te raadplegen.

Dit bewijst de gedistribueerde validatie uit ADR 005: ook als
User Management offline is, blijft deze service operationeel.
"""

import jwt
from flask import Flask, jsonify, request

PUBLIC_KEY_PATH = "/run/secrets/jwt_public_key"

with open(PUBLIC_KEY_PATH, "rb") as f:
    PUBLIC_KEY = f.read()

# Hardcoded challenges voor de POC (data ownership uit ADR 003:
# in productie zou dit een eigen database zijn).
CHALLENGES = [
    {"id": 1, "title": "SQL Injection basics", "difficulty": "beginner"},
    {"id": 2, "title": "XSS reflected attack", "difficulty": "intermediate"},
    {"id": 3, "title": "Buffer overflow", "difficulty": "advanced"},
]

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


@app.route("/challenges", methods=["GET"])
def list_challenges():
    payload, err = validate_token()
    if err:
        return err
    return jsonify(
        {
            "user": payload["sub"],
            "role": payload["role"],
            "challenges": CHALLENGES,
        }
    )


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"service": "challenge-catalog", "status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
