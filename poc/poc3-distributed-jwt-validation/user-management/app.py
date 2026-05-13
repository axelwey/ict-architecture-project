"""
User Management Service - HackLab POC 3

Centrale authenticatieservice die JWT-tokens uitgeeft, ondertekend
met een RSA private key (RS256). Gebaseerd op ADR 005 en de
OAuth-theorieles (authorization server geeft tokens uit).

Deze service is de ENIGE service met toegang tot de private key.
Andere services hebben enkel de public key en valideren zelfstandig.
"""

import time
import json
import jwt
from flask import Flask, jsonify, request

# Private key staat als Docker Swarm secret onder /run/secrets/
# Enkel deze service heeft toegang. Zie poc.yaml.
PRIVATE_KEY_PATH = "/run/secrets/jwt_private_key"

with open(PRIVATE_KEY_PATH, "rb") as f:
    PRIVATE_KEY = f.read()

# Gebruikers worden ingelezen uit een Docker Swarm secret.
# Zelfde patroon als de RSA-keys. Zie poc.yaml en generate-keys.sh.
USERS_PATH = "/run/secrets/users"
with open(USERS_PATH) as f:
    USERS = json.load(f)

TOKEN_EXPIRY_SECONDS = 3600  # 1 uur

app = Flask(__name__)


@app.route("/login", methods=["POST"])
def login():
    """
    Verifieert credentials en geeft een JWT terug.

    De JWT bevat:
      - sub: gebruikersnaam
      - role: rol (student/instructor)
      - iat: issued-at
      - exp: expiry

    Ondertekend met RS256 (asymmetrisch, OAuth-les).
    """
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    user = USERS.get(username)
    if not user or user["password"] != password:
        return jsonify({"error": "Ongeldige gebruikersnaam of wachtwoord"}), 401

    now = int(time.time())
    payload = {
        "sub": username,
        "role": user["role"],
        "iat": now,
        "exp": now + TOKEN_EXPIRY_SECONDS,
    }

    token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")
    return jsonify({"token": token, "expires_in": TOKEN_EXPIRY_SECONDS})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"service": "user-management", "status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
