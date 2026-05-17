# POC 2 — Sandbox Failure Recovery

## 1. Doelstelling en Context

Deze Proof of Concept valideert dat het platform correct reageert wanneer een
sandboxomgeving onverwacht crasht. In een hacking-platform voeren gebruikers
echte exploits uit in geïsoleerde containers. Het is essentieel dat een crash
van één sandbox geen invloed heeft op andere actieve sessies, en dat de
provisioner de fout detecteert en automatisch herstelt.

### Architecturale Link

Deze POC vormt het technische bewijs voor drie cruciale architecturale beslissingen:

- **ADR 001 (Microservices):** Falen blijft geïsoleerd tot één service of container. Een crashende sandbox beïnvloedt de Sandbox Provisioner en andere sandboxen niet.

- **ADR 002 (Communicatie tussen services):** Crash-events worden asynchroon gepubliceerd via **RabbitMQ**. Downstream services zoals een Progress Tracker worden verwittigd zonder directe koppeling aan de provisioner.

- **ADR 004 (Containerisolatie):** Sandbox failure containment werkt in de praktijk. Elke gebruikerssessie draait in een afzonderlijke container die onafhankelijk kan falen.

---

## 2. Technische Componenten

De POC is opgebouwd uit drie services die samenwerken binnen een Docker Swarm-omgeving:

### A. Sandbox Provisioner

- **Technologie:** Python, Flask, Docker SDK, pika.
- **Rol:** Beheert de levenscyclus van sandboxcontainers.
- **Logica:** Start drie sandboxen bij opstart. Een achtergrondthread pollt elke 3 seconden de status van elke container via `container.reload()`. Wanneer een container niet meer `running` is, publiceert de provisioner een `sandbox.crashed`-event, verwijdert de container en start een nieuwe instantie.
- **REST API:** `GET /status` geeft de huidige toestand van alle actieve sandboxen terug.

### B. Message Broker (RabbitMQ)

- **Technologie:** RabbitMQ 3-alpine.
- **Rol:** Asynchrone event-bus tussen de provisioner en downstream services.
- **Configuratie:** Eenvoudige queue `sandbox_events` voor de POC. In productie zou dit een durable exchange met persistent messages zijn.

### C. Event Logger

- **Technologie:** Python, pika.
- **Rol:** Simuleert een downstream service (zoals Progress Tracker of een ops-monitoringsysteem) die reageert op sandbox-events.
- **Logica:** Consumeert berichten van de queue en print elk ontvangen event. Toont aan dat de provisioner en downstream services volledig ontkoppeld zijn via de message broker.

---

## 3. Deployment Instructies

### Clusteropstelling

De testcluster telt drie managers en twee workers. Deze POC draait volledig op de manager nodes. De Sandbox Provisioner beheert containers via de lokale Docker socket (`/var/run/docker.sock`), waardoor de aangemaakte sandboxcontainers op dezelfde node landen als de provisioner. De worker nodes worden in deze POC niet gebruikt: sandbox-isolatie over meerdere nodes vereist een gedistribueerde socket-oplossing die buiten de scope van deze POC valt.

### Vereisten

- Docker met Swarm mode geïnitialiseerd (`docker swarm init`)
- `sudo`-rechten

### Stap 1 — Initialiseer Swarm (indien nog niet gedaan)

```bash
sudo docker swarm init
```

### Stap 2 — Bouw de image

```bash
sudo docker build -t poc2:latest .
```

### Stap 3 — Deploy de stack

```bash
sudo docker stack deploy --compose-file poc.yaml poc
```

### Stap 4 — Controleer of alle services draaien

```bash
sudo docker stack services poc
```

Wacht tot alle services `1/1` tonen onder REPLICAS.

### Opruimen

```bash
sudo docker stack rm poc
sudo docker rm -f $(sudo docker ps -aq --filter "label=managed_by=provisioner")
```

---

## 4. Testen en Validatie

### Status opvragen

Open in de browser of via curl:

```
http://localhost:5000/status
```

Verwachte output:

```json
{
  "sandbox-a": {"id": "<container-id-a>", "state": "running"},
  "sandbox-b": {"id": "<container-id-b>", "state": "running"},
  "sandbox-c": {"id": "<container-id-c>", "state": "running"}
}
```

### Crash simuleren

Haal de container ID op via `/status` en kill de container:

```bash
sudo docker kill <container-id-b>
```

### Logs volgen

```bash
sudo docker service logs poc_provisioner -f
sudo docker service logs poc_event-logger -f
```

### Verwachte output

**Provisioner:**
```
CRASH detected: sandbox-b is exited
Recovering sandbox-b...
Started sandbox-b (nieuw-id)
```

**Event Logger:**
```
[EVENT] sandbox.crashed            sandbox=sandbox-b
[EVENT] sandbox.started            sandbox=sandbox-b
[EVENT] sandbox.recovered          sandbox=sandbox-b
```

Na herstel toont `/status` sandbox-b terug als `running` met een nieuw container ID.

### Wat aangetoond wordt

| Criterium | Verificatie |
|-----------|-------------|
| Crash beperkt tot één sandbox | `/status` toont sandbox-a en sandbox-c als `running` |
| Crash gedetecteerd | provisioner-logs tonen `CRASH detected` |
| Event gepubliceerd | event-logger toont `sandbox.crashed` |
| Automatisch herstel | event-logger toont `sandbox.recovered`, `/status` toont nieuw container ID |