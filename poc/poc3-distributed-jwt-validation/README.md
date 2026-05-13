# POC 3 — Distributed JWT Validation

## Technische vraag

Kan een centrale service JWT-tokens uitgeven (RS256, asymmetrisch),
en kunnen meerdere onafhankelijke services die tokens **zelfstandig**
valideren met enkel de public key — zodat het systeem geen single
point of failure heeft op authenticatie?

## Link met ADR's, theorie en labo's

**ADR 005 — Authenticatie en autorisatie**
> "De uitgifte van tokens is gecentraliseerd in User Management,
> de validatie is gedistribueerd. Elke service valideert binnenkomende
> tokens zelfstandig aan de hand van een gedeelde publieke sleutel."

Deze POC valideert die beslissing.

**Theorieles 9 — OAuth/OIDC**
- JWT als authorization token
- Asymmetrische ondertekening (RS256): private key bij de
  authorization server, public key bij de resource servers
- Concept van resource owner / client / authorization server /
  resource server

**Labo 8 — API gateway**
- Gateway als enkel toegangspunt voor externe clients
- Rate limiting per gebruiker (in labo 8: per geheim)
- Gateway in andere taal dan zuivere JavaScript (hier: Python)

**Labo's 1–6 — Docker Swarm Mode**
- `docker stack deploy -c poc.yaml poc`
- Overlay netwerk voor service-naam-resolutie
- Docker Swarm secrets voor het verspreiden van keys

## Architectuur

```
                 +---------------------+
                 |   User Management   |  (private key)
                 |   poort 8003        |  POST /login
                 +---------------------+
                            |
                            v  uitgifte JWT (RS256)
                       [JWT ondertekend]
                            |
+-----------+      +--------v--------+      +---------------------+
|  client   | ---> |  API Gateway   | ---> |  Challenge Catalog  |
|           |      |  poort 8000    |      |  poort 8001         |
+-----------+      |  (public key)  |      |  (public key)       |
       |           |  rate limit    |      +---------------------+
       |           +----------------+
       |                   |
       |                   v
       |           +---------------------+
       +---------> |  Submission Validator |
        (direct)   |  poort 8002          |
                   |  (public key)        |
                   +---------------------+
```

- **User Management** is de enige service met de private key.
- **Gateway, Catalog en Validator** hebben enkel de public key.
- Elke service valideert tokens zelf, zonder User Management te
  contacteren.
- Keys worden verspreid via **Docker Swarm secrets**.

## Bestandsstructuur

```
poc-3-distributed-jwt-validation/
├── README.md
├── poc.yaml              # Docker Swarm stack file
├── generate-keys.sh      # genereert RSA-keypair
├── build-images.sh       # bouwt de 4 images
├── test-poc.sh           # automatische tests
├── keys/                 # gegenereerde keys (niet in versiebeheer)
├── user-management/      # Flask, gebruikt private key
├── gateway/              # Flask, gebruikt public key + rate limit
├── challenge-catalog/    # Flask, gebruikt public key
└── submission-validator/ # Flask, gebruikt public key
```

## Vereisten

- Docker Engine 20+ in Swarm Mode (`docker swarm init` als nog niet
  actief)
- `openssl` voor key generation
- `curl` en `python3` voor het testscript

**Opmerking:** alle voorbeelden gebruiken `127.0.0.1` in plaats van `localhost`. Docker Swarm publiceert poorten via het ingress-netwerk alleen op IPv4, terwijl `localhost` op recente Ubuntu-systemen eerst naar `::1` (IPv6) resolvet. Met `localhost` lijkt de connectie dan te hangen.

## Opstarten

```bash
# 1) Genereer de RSA-keypair én maak users.json aan
chmod +x generate-keys.sh build-images.sh test-poc.sh
./generate-keys.sh

# 2) Bouw de images (verplicht: docker stack deploy negeert build:)
./build-images.sh

# 3) Initialiseer Swarm Mode indien nog niet actief
docker swarm init 2>/dev/null || true

# 4) Deploy de stack
docker stack deploy -c poc.yaml poc

# 5) Wacht tot alle services up zijn
docker stack services poc
```

## Manuele teststappen

### 1. Login en token ophalen

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8003/login \
    -H "Content-Type: application/json" \
    -d '{"username":"student","password":"student123"}' \
    | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")
echo $TOKEN
```

### 2. Via gateway (synchroon, met rate limiting)

```bash
curl http://127.0.0.1:8000/challenges -H "Authorization: Bearer $TOKEN"
```

### 3. Direct bij Catalog — bewijst gedistribueerde validatie

```bash
curl http://127.0.0.1:8001/challenges -H "Authorization: Bearer $TOKEN"
```

De Catalog antwoordt zonder User Management te contacteren.

### 4. Direct bij Validator — idem

```bash
curl -X POST http://127.0.0.1:8002/submit \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"challenge_id":1,"flag":"FLAG{sql_injection_basics}"}'
```

### 5. KERNTEST — User Management uitschakelen

```bash
docker service scale poc_user-management=0
sleep 5

# Catalog en Validator moeten blijven werken met het bestaande token:
curl http://127.0.0.1:8001/challenges -H "Authorization: Bearer $TOKEN"
curl -X POST http://127.0.0.1:8002/submit \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"challenge_id":1,"flag":"FLAG{sql_injection_basics}"}'

# Terug aanzetten:
docker service scale poc_user-management=1
```

Dit is **het bewijs** dat ADR 005 levert: er is geen runtime-
afhankelijkheid van de centrale service voor validatie.

### 6. Vervalst token

```bash
FORGED="${TOKEN%?}X"  # laatste karakter wijzigen
curl http://127.0.0.1:8001/challenges -H "Authorization: Bearer $FORGED"
# -> 401, signature klopt niet
```

### 7. Rate limit (5 requests / minuut)

```bash
for i in {1..7}; do
    curl -s -o /dev/null -w "%{http_code}\n" \
        http://127.0.0.1:8000/challenges \
        -H "Authorization: Bearer $TOKEN"
done
# -> 200 200 200 200 200 429 429
```

## Geautomatiseerde test

```bash
./test-poc.sh
```

Dit script doorloopt alle scenario's hierboven en geeft groen/rood feedback.

## Opruimen

```bash
docker stack rm poc
```

## Wat deze POC bewijst

- **Centrale uitgifte** van tokens werkt (User Management, RS256)
- **Gedistribueerde validatie** werkt: drie services valideren
  zelfstandig met enkel de public key
- **Geen single point of failure**: User Management offline =
  catalog en validator blijven operationeel
- **Vervalste tokens** worden door alle services geweigerd
- **Rate limiting** in de gateway werkt (labo 8 patroon)

Hiermee is ADR 005 valideerbaar.
