# POC 4: Asynchrone Voortgangsregistratie

**Valideert:** ADR 002 (Hybride communicatie), ADR 003 (Data ownership)

## Doel

Deze POC toont aan dat een flag-indiening asynchroon verwerkt kan worden:  
de student krijgt onmiddellijk een resultaat terug, terwijl de  
voortgangsregistratie op de achtergrond via RabbitMQ verloopt. De twee  
verantwoordelijkheden validatie en opslag zijn strikt gescheiden en  
communiceren uitsluitend via een message queue.

## Componenten

| Service | Rol |
| --- | --- |
| `rabbitmq` | Message broker. Bewaart events op de queue `flag.submitted`. |
| `producer` | Submission Validator. Valideert de flag en publiceert een event. |
| `consumer` | Progress Tracker. Consumeert het event en werkt de voortgang bij. |

### Producer (`producer.js`)

Exposeert een REST-endpoint `POST /submit`. Bij ontvangst van een verzoek:

1.  Valideert de ingediende flag aan de hand van een vaste tabel met correcte antwoorden.
2.  Stuurt **onmiddellijk** een JSON-antwoord terug (`{ "correct": true/false, "timestamp": "..." }`).
3.  Publiceert daarna een persistent event op de queue `flag.submitted`.

De beschikbare challenges en hun flags:

| Challenge ID | Correcte flag |
| --- | --- |
| `challenge-001` | `FLAG{sql_injection_mastered}` |
| `challenge-002` | `FLAG{xss_reflected_found}` |
| `challenge-003` | `FLAG{rce_via_deserialization}` |

### Consumer (`consumer.js`)

Luistert continu op de queue `flag.submitted`. Bij ontvangst van een event:

1.  Wacht vijf seconden (gesimuleerde database-write).
2.  Werkt de in-memory voortgang bij voor de betreffende gebruiker.
3.  Logt het totaal aantal opgeloste challenges voor die gebruiker.

Beide services proberen bij opstart maximaal tien keer verbinding te maken  
met RabbitMQ, met een wachttijd van drie seconden tussen pogingen. Dit  
vangt het geval op waarbij RabbitMQ nog niet klaar is wanneer de services  
starten.

## Opstarten

Docker Swarm bouwt images niet zelf. Gebruik het meegeleverde script om de  
images te bouwen en de stack te deployen:

```bash
cd poc4-Asynchrone-Voortgangsregistratie
chmod +x start.sh
./start.sh
```

Of voer het handmatig uit:

```bash
docker build -t poc4-producer:latest ./producer
docker build -t poc4-consumer:latest ./consumer
docker stack deploy -c poc.yml poc4
```

Wacht tot alle services actief zijn:

```bash
docker stack services poc4
```

Alle drie services moeten de status `1/1` tonen voordat je verder gaat.

## Demonstratie

### Stap 1: Volg de logs van de consumer

Open een tweede terminal en volg de uitvoer van de Progress Tracker:

```bash
docker service logs -f poc4_consumer
```

### Stap 2: Dien een correcte flag in

```bash
curl -s -X POST http://localhost:3000/submit \
  -H "Content-Type: application/json" \
  -d '{"userId": "student-42", "challengeId": "challenge-001", "flag": "FLAG{sql_injection_mastered}"}' \
  | jq
```

Verwacht antwoord (onmiddellijk):

```json
{
  "correct": true,
  "timestamp": "2025-05-17T10:00:00.000Z"
}
```

In de consumer-logs verschijnt vijf seconden later:

```
[consumer] event ontvangen: student-42 → challenge-001
[consumer] wacht 5s (simuleert DB-write)...
[consumer] voortgang bijgewerkt: student-42 heeft 1 challenge(s) opgelost
```

### Stap 3: Dien een foute flag in

```bash
curl -s -X POST http://localhost:3000/submit \
  -H "Content-Type: application/json" \
  -d '{"userId": "student-42", "challengeId": "challenge-002", "flag": "FLAG{wrong}"}' \
  | jq
```

Verwacht antwoord:

```json
{
  "correct": false,
  "timestamp": "2025-05-17T10:00:05.000Z"
}
```

Er wordt ook bij een fout antwoord een event gepubliceerd, zodat de  
Progress Tracker mislukte pogingen kan registreren.

### Stap 4: Toon dat events niet verloren gaan bij uitval

Stop de consumer tijdelijk:

```bash
docker service scale poc4_consumer=0
```

Dien een nieuwe flag in:

```bash
curl -s -X POST http://localhost:3000/submit \
  -H "Content-Type: application/json" \
  -d '{"userId": "student-99", "challengeId": "challenge-003", "flag": "FLAG{rce_via_deserialization}"}' \
  | jq
```

De producer antwoordt nog steeds onmiddellijk. Start de consumer opnieuw:

```bash
docker service scale poc4_consumer=1
```

In de logs is te zien dat het event alsnog verwerkt wordt RabbitMQ  
heeft het bericht bewaard terwijl de consumer offline was.

## Opruimen

```bash
docker stack rm poc4
```
