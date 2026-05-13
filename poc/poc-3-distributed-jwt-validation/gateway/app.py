"""
API Gateway - HackLab POC 3

Enkel toegangspunt voor externe clients. Valideert JWT-tokens LOKAAL
met de public key (zonder de User Management service te contacteren).
Past rate limiting toe per gebruiker.

Gebaseerd op:
  - Labo 8 (API gateway voorzien): rate limiting, gateway als facade
  - OAuth-theorieles: lokale tokenvalidatie via public key
  - ADR 005: gedistribueerde validatie, geen single point of failure
"""

import time
from collections import defaultdict
from threading import Lock

import jwt
import requests
from flask import Flask, jsonify, request, Response

# Public key staat als Docker Swarm secret onder /run/secrets/
# Deze service heeft enkel de PUBLIC key (kan valideren, niet ondertekenen).
PUBLIC_KEY_PATH = "/run/secrets/jwt_public_key"

with open(PUBLIC_KEY_PATH, "rb") as f:
    PUBLIC_KEY = f.read()

# Rate limiting: maximaal 5 requests per minuut per gebruiker.
# Gebaseerd op labo 8: "rate limit waarbij elk geheim maar twee keer
# per minuut gebruikt kan worden". Voor de POC verhoogd naar 5/minuut
# om realistischer testen toe te laten.
RATE_LIMIT = 5
WINDOW_SECONDS = 60

request_log = defaultdict(list)
rate_lock = Lock()

# Achterliggende services bereikbaar via service-naam in het overlay
# netwerk (Docker Swarm). Zie poc.yaml.
CATALOG_URL = "http://challenge-catalog:3000"
VALIDATOR_URL = "http://submission-validator:3000"

app = Flask(__name__)


def validate_token():
    """
    Valideert het JWT-token in de Authorization header.
    Geeft (payload, None) terug bij succes, of (None, error_response).
    """
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


def check_rate_limit(user):
    """In-memory rate limiter per gebruiker (sliding window)."""
    with rate_lock:
        now = time.time()
        request_log[user] = [
            t for t in request_log[user] if now - t < WINDOW_SECONDS
        ]
        if len(request_log[user]) >= RATE_LIMIT:
            return False
        request_log[user].append(now)
        return True


def proxy(method, target_url, json_body=None):
    """Forward het request inclusief Authorization header."""
    headers = {"Authorization": request.headers["Authorization"]}
    try:
        if method == "GET":
            r = requests.get(target_url, headers=headers, timeout=5)
        else:
            r = requests.post(
                target_url, json=json_body, headers=headers, timeout=5
            )
    except requests.RequestException as e:
        return jsonify({"error": f"Backend onbereikbaar: {e}"}), 502

    return Response(
        r.content,
        status=r.status_code,
        content_type=r.headers.get("Content-Type", "application/json"),
    )


@app.route("/challenges", methods=["GET"])
def challenges():
    payload, err = validate_token()
    if err:
        return err
    if not check_rate_limit(payload["sub"]):
        return jsonify({"error": "Rate limit overschreden"}), 429

    return proxy("GET", f"{CATALOG_URL}/challenges")


@app.route("/submit", methods=["POST"])
def submit():
    payload, err = validate_token()
    if err:
        return err
    if not check_rate_limit(payload["sub"]):
        return jsonify({"error": "Rate limit overschreden"}), 429

    return proxy("POST", f"{VALIDATOR_URL}/submit", json_body=request.get_json())


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"service": "gateway", "status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
