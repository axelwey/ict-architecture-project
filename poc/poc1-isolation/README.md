# POC 1 — Sandbox Isolation & Resource Limiting

## Doel

Deze Proof of Concept valideert ADR 004 (Isolatie van sandbox-omgevingen).

Het doel is aan te tonen dat Docker-containers gebruikt kunnen worden als veilige sandboxomgevingen voor gebruikers die code, scripts of exploits uitvoeren binnen het HackLab-platform.

De POC demonstreert:

- isolatie tussen sandbox en host-systeem
- beperkte rechten binnen de container
- CPU- en geheugenlimieten
- automatische opruiming van sandboxen
- bescherming van het hostsysteem tegen resource exhaustion

---

# Architecturale link

## ADR 004 — Isolatie van sandbox-omgevingen

Deze POC ondersteunt de keuze voor containerisolatie via Docker.

De test toont aan dat:

- gebruikersprocessen geïsoleerd blijven
- resourcegebruik gecontroleerd kan worden
- containers veilig vernietigd kunnen worden na gebruik

Ondersteunde karakteristieken:

- Security
- Fault Tolerance
- Availability

---

# Vereisten

- Docker Desktop of Docker Engine
- Linux / WSL / Debian omgeving

Controleer of Docker actief is:

```bash
docker --version
