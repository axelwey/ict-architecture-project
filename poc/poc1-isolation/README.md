# POC 1 — Container Isolation & Resource Limiting

## Doel

Deze Proof of Concept valideert ADR 004 (Isolatie van sandbox-omgevingen).

Het doel van deze POC is aan te tonen dat Docker-containers gebruikt kunnen worden als veilige en geïsoleerde sandboxomgevingen binnen het HackLab-platform.

Gebruikers voeren binnen het platform potentieel onbetrouwbare code, scripts en exploits uit. Daarom moet elke sandboxomgeving:

- geïsoleerd zijn van andere sandboxen
- geen elevated privileges hebben
- beperkte resources gebruiken
- geen directe toegang hebben tot het hostsysteem
- automatisch verwijderd kunnen worden na gebruik

Deze POC demonstreert dat Docker deze eigenschappen kan ondersteunen.

---

# Architecturale link

## ADR 004 — Isolatie van sandbox-omgevingen

Deze POC ondersteunt de keuze voor containerisolatie via Docker.

De test toont aan dat:

- gebruikersprocessen geïsoleerd blijven
- resourcegebruik gecontroleerd kan worden
- sandboxen geen elevated privileges krijgen
- sandboxen automatisch verwijderd kunnen worden
- het hostsysteem beschermd blijft tegen resource exhaustion

Ondersteunde karakteristieken:

- Security
- Fault Tolerance
- Availability

---

# Structuur van de POC

De POC bestaat uit:

- een Docker-container die dient als sandboxomgeving
- resource limiting via Docker Swarm
- privilege beperking via security opties
- een intern overlay-netwerk zonder externe toegang
- een stress test die memory exhaustion simuleert

---

# Bestandsstructuur

```text
poc1-isolation/
├── Dockerfile
├── poc.yaml
├── README.md
├── stress_test.py
└── screenshots/
