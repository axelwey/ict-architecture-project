# POC 4 — Asynchrone Voortgangsregistratie

## 1\. Doelstelling en Context

Deze Proof of Concept (POC) valideert de implementatie van een **niet-blokkerende gebruikerservaring** bij het indienen van challenge-oplossingen. In een hacking-platform is het essentieel dat een student direct feedback krijgt over zijn actie (vlag goed/fout), terwijl de zwaardere verwerking (zoals het bijwerken van scores en voortgang in een database) veilig op de achtergrond gebeurt.

### Architecturale Link

Deze POC vormt het technische bewijs voor twee cruciale architecturale beslissingen:

- **ADR 002 (Communicatie tussen services):** Gebruik van een hybride model. Synchrone HTTP-communicatie voor de interactie met de student en asynchrone berichtuitwisseling via **RabbitMQ** voor de interne systeemafhandeling.
    
- **ADR 003 (Data ownership per service):** De Submission Validator en de Progress Tracker delen geen database. Data wordt overgedragen via events, waardoor de services volledig ontkoppeld zijn.
    

* * *

## 2\. Technische Componenten

De POC is opgebouwd uit drie actieve containers die samenwerken binnen een Docker Swarm-omgeving:

### A. Submission Validator (Producer)

- **Technologie:** Node.js, Express, `amqplib`.
    
- **Rol:** Ontvangt de vlag van de student.
    
- **Logica:** In `producer.js` wordt de vlag onmiddellijk gecontroleerd tegen een lokale lijst (in productie is dit een eigen database).
    
- **Asynchroon gedrag:** Het HTTP-antwoord (`res.json`) wordt verstuurd **voordat** het bericht naar de queue gaat. Hierdoor ervaart de gebruiker nul vertraging door netwerk- of database-latency in de backend.
    

### B. Message Broker (RabbitMQ)

- **Technologie:** RabbitMQ 3.13 (Management-Alpine).
    
- **Rol:** De betrouwbare tussenpersoon.
    
- **Configuratie:** Gebruikt een `durable` queue en `persistent` berichten om te garanderen dat er geen voortgangsdata verloren gaat, zelfs niet bij een tijdelijke uitval van de consument.
    

### C. Progress Tracker (Consumer)

- **Technologie:** Node.js, `amqplib`.
    
- **Rol:** Verwerkt de resultaten op de achtergrond.
    
- **Logica:** Om een zware database-transactie te simuleren, bevat `consumer.js` een kunstmatige vertraging van **5 seconden** (`DELAY_MS`). Pas na deze tijd wordt de voortgang bijgewerkt.
    

* * *

## 3\. Deployment Instructies

## 4\. Testen en Validatie

```
curl -X POST http://localhost:3000/submit -H "Content-Type: application/json" -d '{"userId":"student-1","challengeId":"challenge-001","flag":"FLAG{sql_injection_mastered}"}'
```

&nbsp;
