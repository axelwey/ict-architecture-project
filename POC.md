Beschrijving van de verschillende POC's

# 1\. Sandbox Isolatie & Resource Limiting

> Bewijzen dat een gebruiker die een exploit uitvoert in een container (ADR 004) niet de host kan overnemen of alle resources kan opgebruiken.

&nbsp;   Architecturale link: Security & Fault Tolerance.

&nbsp;   Implementatie:

&nbsp;       Maak een Python-script dat de Docker SDK gebruikt om een "slachtoffer-container" op te starten.

&nbsp;       Configureer deze container met strikte mem_limit (bijv. 64MB) en cpu_period/cpu_quota.

&nbsp;       Voeg een test-script toe in de container dat een fork bomb of een geheugenvreter uitvoert.

&nbsp;       Resultaat: Toon aan dat de container gecrasht wordt door de Docker Daemon (OOM-killer) of beperkt wordt in CPU, zonder dat de host-machine (je eigen laptop/server) vertraagt.

# 2\. Asynchrone Voortgangsregistratie

> Valideren van de hybride communicatie (ADR 002) waarbij een ingediende flag via een message broker de voortgang bijwerkt zonder dat de gebruiker blokkeert.

&nbsp;   Architecturale link: Scalability & Availability.

&nbsp;   Implementatie:

&nbsp;       Zet een kleine RabbitMQ service op in een docker-compose (voor de POC).

&nbsp;       Maak twee kleine Node.js scriptjes: SubmissionService (Producer) en ProgressTracker (Consumer).

&nbsp;       Wanneer de Producer een flag "ontvangt", stuurt hij direct een "OK" terug naar de (gesimuleerde) client, maar plaatst hij een event op de queue.

&nbsp;       De Consumer verwerkt dit event met een kunstmatige vertraging van 5 seconden.

&nbsp;       Resultaat: Toon aan dat de student direct verder kan, terwijl de database-update van de score veilig op de achtergrond gebeurt.

# 3\. Gedistribueerde JWT Validatie

> Bewijzen dat services onafhankelijk tokens kunnen valideren zonder de User Service telkens aan te roepen (ADR 005).

Architecturale link: Security & Scalability.

&nbsp;   Implementatie:

&nbsp;       Maak een script dat een JWT genereert en ondertekent met een RS256 Private Key.

&nbsp;       Maak een tweede, volledig losstaande service (bijv. de ChallengeCatalog) die enkel de Public Key heeft.

&nbsp;       Stuur het token naar de tweede service.

&nbsp;       Resultaat: Toon aan dat de tweede service kan verifiëren wie de gebruiker is en welke rol (Student/Admin) hij heeft, puur op basis van cryptografie, zonder netwerkverbinding met de Identity service.

# 4\. Dynamic Container Proxying (The Challenge Interface)

> Hoe verbind je de browser van een student met een terminal in een specifiek voor hem opgestarte Docker container?

Architecturale link: Configurability & User Experience.

Implementatie:

&nbsp;       Gebruik xterm.js voor de frontend (een terminal in de browser).

&nbsp;       Gebruik Socket.io of pure WebSockets om de verbinding naar een Node.js backend te leggen.

&nbsp;       Gebruik de docker.getContainer(id).exec() functie van de Docker SDK om een interactieve shell (/bin/bash) te koppelen aan de WebSocket stream.

&nbsp;       Resultaat: Een student typt in zijn browser en ziet direct de output van de geïsoleerde sandbox.

# poc mappen structuur

Volgens de opdracht moet elke POC in een eigen map staan met een README.md en een poc.yaml.

voorbeeld mappenstructuur:

```
/poc1-isolation/  
  ├── poc.yaml (Docker Stack file)  
  ├── Dockerfile  
  ├── app.py  
  └── README.md (Leg uit: "Run 'docker exec -it [container] python test_exploit.py'")

/poc2-messaging/  
  ├── poc.yaml (Inclusief RabbitMQ image)  
  ├── producer.js  
  ├── consumer.js  
  └── README.md
```
