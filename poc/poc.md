# Proofs of Concept

Elke POC bewijst één specifieke architecturale beslissing in isolatie.
Ze zijn bewust klein gehouden: geen volledige frontend, geen uitgebreide
configuratiebestanden, geen productie-monitoring. Het doel is telkens één
concrete technische vraag beantwoorden. Elke POC staat in een aparte map
en kan worden opgestart via:

```bash
docker stack deploy -f poc.yaml poc
```

Sommige POC's vereisen daarna een handmatige stap via `docker exec`; dit
wordt beschreven in de `README.md` van de betreffende map.

---

## POC 1: Sandbox Isolatie & Resource Limiting

**Valideert:** ADR 004 (Sandbox-isolatie via Docker)  
**Architecturale link:** Security, Fault Tolerance

### Probleemstelling

Gebruikers voeren echte exploits en aanvalscode uit op het platform. De
centrale vraag is: kan een gebruiker die kwaadaardige of ongecontroleerde
code uitvoert binnen zijn container, de host-machine of andere
gebruikerscontainers bereiken of overbelasten?

### Wat wordt aangetoond

- Een container draait zonder `--privileged`-flag en met een beperkt
  `seccomp`-profiel.
- CPU- en geheugenlimieten worden afgedwongen via Docker resource
  constraints.
- Een gesimuleerde memory-exhaustion of CPU-bomb wordt tegengehouden door
  de Docker-daemon (OOM-killer of CPU-throttling), zonder merkbare impact
  op de host.
- De container kan niet communiceren met andere containers op het
  platform-netwerk.

### Implementatie

Een kleine Python-applicatie (`app.py`) exposeert twee endpoints:

- `/cpu-bomb`: start een oneindige berekeningslus.
- `/memory-bomb`: alloceert geheugen totdat de OOM-killer ingrijpt.

De container wordt gestart met expliciete limieten (`mem_limit`,
`cpus`). De tester voert de aanval uit via `docker exec` en observeert dat
de container gekilld of gethrottled wordt, terwijl de host normaal blijft
functioneren.

### Verwacht resultaat

De Docker-daemon beëindigt of throttelt de container bij overschrijding van
de resourcelimieten. De host-machine vertraagt niet. Een poging om buiten de
container te geraken (bijv. via `/proc/1/ns`) mislukt met een
`permission denied`-fout.

---

## POC 2: Sandbox Failure Recovery

**Valideert:** ADR 001 (Microservices), ADR 004 (Sandbox-isolatie)  
**Architecturale link:** Fault Tolerance, Availability

### Probleemstelling

Een sandbox-container kan crashen door een gebruikersfout, een exploit of
een systeemfout. De architectuur stelt dat zulke fouten beperkt moeten
blijven tot de betrokken sandbox en dat het systeem zichzelf kan herstellen.
De vraag is: detecteert de Sandbox Provisioner een crash, en blijven andere
sandboxen operationeel?

### Wat wordt aangetoond

- Meerdere sandbox-containers draaien gelijktijdig.
- Eén container wordt geforceerd beëindigd (`docker kill`) of brengt
  zichzelf in een faulted state.
- De overige containers blijven bereikbaar.
- Een Provisioner-service detecteert de crash via een Docker-event
  (`container die`) en publiceert een `sandbox.crashed`-event op de
  message broker.
- De Provisioner herstart de container automatisch op basis van dat event.

### Implementatie

Drie services in de stack:

- **sandbox-a, sandbox-b**: eenvoudige HTTP-servers die bereikbaarheid
  bevestigen via een `/health`-endpoint.
- **provisioner**: luistert naar de Docker socket en naar de RabbitMQ-queue.
  Bij een `container die`-event publiceert hij een bericht en herstart hij
  de betreffende container.

De tester voert `docker kill poc_sandbox-a.1.*` uit en verifieert dat
`sandbox-b` bereikbaar blijft en dat `sandbox-a` na enkele seconden
automatisch herstart.

### Verwacht resultaat

- `sandbox-b` reageert correct op `/health` tijdens en na de crash van
  `sandbox-a`.
- De Provisioner logt het `sandbox.crashed`-event.
- `sandbox-a` is na automatisch herstel opnieuw bereikbaar.

---

## POC 3: Gedistribueerde JWT-validatie

**Valideert:** ADR 005 (Authenticatie en autorisatie)  
**Architecturale link:** Security, Scalability

### Probleemstelling

Elke service moet weten wie een verzoek verstuurt en welke rol die gebruiker
heeft (Student of Admin). Een naïeve aanpak laat elke service de Identity
Service aanroepen bij elk verzoek. Dit introduceert een single point of
failure en verhoogt de latentie. De vraag is: kan een service een token
zelfstandig valideren, zonder runtime-afhankelijkheid van de centrale Identity
Service?

### Wat wordt aangetoond

- De Identity Service genereert een JWT ondertekend met een RSA private key
  (RS256).
- Een tweede service (Resource Service) valideert het token uitsluitend met
  de bijhorende public key, zonder netwerkverbinding met de Identity Service.
- De Resource Service extraheert de gebruikersrol uit de token-claims en
  past toegangscontrole toe.
- Een token met een ongeldig handtekening of een verlopen token wordt
  geweigerd.

### Implementatie

Twee services:

- **identity-service**: ontvangt een login-verzoek, genereert een JWT
  (RS256, `sub`, `role`, `exp`) en retourneert dit aan de client.
- **resource-service**: ontvangt een verzoek met een `Authorization: Bearer
  <token>`-header, valideert het token met de ingebakken public key en
  retourneert de beschermde resource als de rol correct is.

De private en public key worden gegenereerd bij het bouwen van de container.
De public key wordt als environment variable meegegeven aan de
resource-service.

### Verwacht resultaat

- Een geldig token geeft toegang tot de beschermde resource.
- Een token met een ongeldige handtekening retourneert HTTP 401.
- Een verlopen token retourneert HTTP 401.
- Er is geen enkel netwerkverkeer tussen `resource-service` en
  `identity-service` tijdens de validatie.

---

## POC 4: Asynchrone Voortgangsregistratie

**Valideert:** ADR 002 (Hybride communicatie), ADR 003 (Data ownership)  
**Architecturale link:** Scalability, Availability

### Probleemstelling

Wanneer een student een flag indient, moet de voortgang worden bijgewerkt in
de Progress Tracker. Die update hoeft niet te voltooien voordat de student
zijn resultaat te zien krijgt. De vraag is: kan de Submission Validator
direct antwoord geven aan de client, terwijl de Progress Tracker
asynchroon en onafhankelijk zijn database bijwerkt?

### Wat wordt aangetoond

- De Submission Validator valideert een ingediende flag en retourneert
  onmiddellijk een resultaat aan de client.
- Tegelijkertijd plaatst hij een `flag.submitted`-event op een
  RabbitMQ-queue.
- De Progress Tracker consumeert dit event en werkt zijn eigen datastore bij
  met een kunstmatige vertraging van vijf seconden.
- Tijdelijke uitval van de Progress Tracker verliest geen events: RabbitMQ
  bewaart de berichten totdat de consumer hervat.

### Implementatie

Drie services:

- **submission-validator** (Node.js): exposeert een `POST /submit`-endpoint.
  Valideert de flag, antwoordt onmiddellijk met `{ "result": "correct" }` of
  `{ "result": "incorrect" }` en plaatst bij een correcte flag een event op
  de queue.
- **progress-tracker** (Node.js): luistert op de queue, wacht vijf seconden
  (gesimuleerde verwerking) en logt de update van de voortgang.
- **rabbitmq**: standaard RabbitMQ-image met management-plugin.

### Verwacht resultaat

- De client ontvangt het resultaat binnen milliseconden na indiening.
- De Progress Tracker logt de update vijf seconden later, onafhankelijk van
  de client.
- Bij tijdelijke uitval van de Progress Tracker (gestopt en herstart via
  `docker service scale`) gaan geen events verloren: de queue bewaart
  openstaande berichten.


