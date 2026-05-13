#!/bin/bash
# Geautomatiseerde tests voor POC 3 - Distributed JWT Validation.
#
# Doorloopt alle scenario's die ADR 005 valideren:
#   1. Login en token verkrijgen
#   2. Gebruik token via gateway (synchroon, met rate limiting)
#   3. Gebruik token DIRECT bij catalog (gedistribueerde validatie)
#   4. Gebruik token DIRECT bij validator (gedistribueerde validatie)
#   5. User Management offline -> catalog/validator blijven werken
#   6. Vervalst token wordt door alle services geweigerd
#   7. Rate limit op de gateway

set -e

GATEWAY="http://127.0.0.1:8000"
CATALOG="http://127.0.0.1:8001"
VALIDATOR="http://127.0.0.1:8002"
USERMGMT="http://127.0.0.1:8003"

GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[1;33m"
NC="\033[0m"

ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
fail() { echo -e "${RED}[FOUT]${NC} $1"; exit 1; }
info() { echo -e "${YELLOW}=== $1 ===${NC}"; }


info "1. Login bij User Management"
TOKEN=$(curl -s -X POST $USERMGMT/login \
    -H "Content-Type: application/json" \
    -d '{"username":"student","password":"student123"}' \
    | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")

if [ -z "$TOKEN" ]; then
    fail "Geen token ontvangen"
fi
ok "Token ontvangen (lengte ${#TOKEN})"


info "2. Challenges opvragen via de Gateway (met geldig token)"
RESP=$(curl -s -w "\n%{http_code}" $GATEWAY/challenges \
    -H "Authorization: Bearer $TOKEN")
CODE=$(echo "$RESP" | tail -n1)
if [ "$CODE" != "200" ]; then
    fail "Gateway gaf $CODE in plaats van 200"
fi
ok "Gateway accepteerde token en gaf 200"


info "3. Challenges DIRECT opvragen bij Catalog (zonder gateway)"
RESP=$(curl -s -w "\n%{http_code}" $CATALOG/challenges \
    -H "Authorization: Bearer $TOKEN")
CODE=$(echo "$RESP" | tail -n1)
if [ "$CODE" != "200" ]; then
    fail "Catalog gaf $CODE in plaats van 200"
fi
ok "Catalog valideerde het token zelfstandig (gedistribueerde validatie)"


info "4. Flag indienen DIRECT bij Validator (zonder gateway)"
RESP=$(curl -s -w "\n%{http_code}" -X POST $VALIDATOR/submit \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"challenge_id":1,"flag":"FLAG{sql_injection_basics}"}')
CODE=$(echo "$RESP" | tail -n1)
if [ "$CODE" != "200" ]; then
    fail "Validator gaf $CODE in plaats van 200"
fi
ok "Validator valideerde het token zelfstandig (gedistribueerde validatie)"


info "5. User Management UITSCHAKELEN -> catalog/validator moeten blijven werken"
docker service scale poc_user-management=0 > /dev/null
sleep 5

RESP=$(curl -s -w "\n%{http_code}" $CATALOG/challenges \
    -H "Authorization: Bearer $TOKEN")
CODE=$(echo "$RESP" | tail -n1)
if [ "$CODE" != "200" ]; then
    fail "Catalog faalde terwijl User Management offline was (code $CODE)"
fi
ok "Catalog werkt nog zonder User Management"

RESP=$(curl -s -w "\n%{http_code}" -X POST $VALIDATOR/submit \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"challenge_id":1,"flag":"FLAG{sql_injection_basics}"}')
CODE=$(echo "$RESP" | tail -n1)
if [ "$CODE" != "200" ]; then
    fail "Validator faalde terwijl User Management offline was (code $CODE)"
fi
ok "Validator werkt nog zonder User Management"
ok "ADR 005 bevestigd: geen single point of failure"

# User Management terug aanzetten voor verdere tests
docker service scale poc_user-management=1 > /dev/null
sleep 5


info "6. Vervalst token (payload aangepast om admin-rechten te claimen)"
# Realistische aanval: gebruiker wijzigt zijn eigen role naar 'admin'
# Zonder de private key kan de signature niet meegewijzigd worden,
# dus services moeten dit weigeren.
FORGED=$(TOKEN="$TOKEN" python3 << 'PYEOF'
import base64, json, os
token = os.environ['TOKEN']
parts = token.split(".")
header = parts[0]
sig = parts[2]
malicious = base64.urlsafe_b64encode(
    json.dumps({"sub": "student", "role": "admin", "iat": 0, "exp": 9999999999}).encode()
).decode().rstrip("=")
print(f"{header}.{malicious}.{sig}")
PYEOF
)
export TOKEN
RESP=$(curl -s -w "\n%{http_code}" $CATALOG/challenges \
    -H "Authorization: Bearer $FORGED")
CODE=$(echo "$RESP" | tail -n1)
if [ "$CODE" != "401" ]; then
    fail "Catalog accepteerde een vervalst token (code $CODE)!"
fi
ok "Catalog weigerde vervalst token (401)"

RESP=$(curl -s -w "\n%{http_code}" -X POST $VALIDATOR/submit \
    -H "Authorization: Bearer $FORGED" \
    -H "Content-Type: application/json" \
    -d '{"challenge_id":1,"flag":"x"}')
CODE=$(echo "$RESP" | tail -n1)
if [ "$CODE" != "401" ]; then
    fail "Validator accepteerde een vervalst token (code $CODE)!"
fi
ok "Validator weigerde vervalst token (401)"


info "7. Rate limit testen op Gateway (5 requests/min, labo 8 patroon)"
HIT_LIMIT=0
for i in 1 2 3 4 5 6 7; do
    CODE=$(curl -s -o /dev/null -w "%{http_code}" $GATEWAY/challenges \
        -H "Authorization: Bearer $TOKEN")
    if [ "$CODE" = "429" ]; then
        HIT_LIMIT=1
        ok "Rate limit getriggered op request $i (429)"
        break
    fi
done
if [ "$HIT_LIMIT" = "0" ]; then
    fail "Rate limit werd niet getriggered binnen 7 requests"
fi


echo
echo -e "${GREEN}Alle tests geslaagd. POC 3 valideert ADR 005.${NC}"
