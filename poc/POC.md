Beschrijving van de verschillende POC's

# 1\. Sandbox Isolatie & Resource Limiting (anwar)

> Bewijzen dat een gebruiker die een exploit uitvoert in een container (ADR 004) niet de host kan overnemen of alle resources kan opgebruiken.

&nbsp;   Architecturale link: Security & Fault Tolerance.

Voor deze opdracht zal een Proof of Concept uitgewerkt worden die test of het mogelijk is om veilige en geïsoleerde labomgevingen te creëren met behulp van Docker-containers. Het doel is om aan te tonen dat gebruikers in een sandboxomgeving kunnen werken zonder invloed te hebben op andere gebruikers of het onderliggende systeem.

Concreet zal een container opgezet worden met een kwetsbare applicatie waarin een gebruiker acties kan uitvoeren. Daarbij wordt aangetoond dat de container geïsoleerd draait, beperkte rechten heeft (geen privileged mode, beperkte resources) en automatisch kan worden gestopt na gebruik. Dit bewijst dat het systeem veilige sandboxomgevingen kan aanbieden, wat essentieel is voor een platform waarin hacking-oefeningen worden uitgevoerd

&nbsp;       Resultaat: Toon aan dat de container gecrasht wordt door de Docker Daemon (OOM-killer) of beperkt wordt in CPU, zonder dat de host-machine (je eigen laptop/server) vertraagt of dat de gebruiker hier buiten kan.

# 2\. Sandbox Failure Recovery (jasper)

Voor deze opdracht wordt een Proof of Concept uitgewerkt die test of het systeem correct reageert wanneer een sandboxomgeving onverwacht crasht of vastloopt.

Het doel is aan te tonen dat:

· een crash beperkt blijft tot de betrokken sandbox

· andere actieve sandboxen operationeel blijven

· de Sandbox Provisioner de fout detecteert

· automatisch herstel of heropstart mogelijk is

Concreet worden meerdere sandboxcontainers gestart. Eén container wordt geforceerd beëindigd of in een fault-state gebracht. Vervolgens wordt gecontroleerd of:

· de andere containers bereikbaar blijven

· de crash correct wordt gedetecteerd

· een event wordt gepubliceerd

· de container automatisch vervangen kan worden

Link met ADR’s

ADR 001 (Microservices) Valideert dat falen geïsoleerd blijft.

ADR 004 (Sandbox Isolatie) Toont dat sandbox failure containment werkt.

# 3\. Gedistribueerde JWT Validatie (axel)

> Bewijzen dat services onafhankelijk tokens kunnen valideren zonder de User Service telkens aan te roepen (ADR 005).

Architecturale link: Security & Scalability.

Voor deze opdracht zal een Proof of Concept uitgewerkt worden die test hoe gebruikers veilig kunnen worden beheerd binnen het systeem. Het doel is om aan te tonen dat authenticatie en autorisatie correct functioneren en dat gebruikersgegevens veilig worden opgeslagen.

Concreet zal een login-systeem geïmplementeerd worden met behulp van JWT-authenticatie. Gebruikers kunnen zich aanmelden en ontvangen een token dat gebruikt wordt bij verdere interacties met het systeem. Daarnaast wordt de voortgang van de gebruiker opgeslagen in een aparte datastore.

Link met ADR 005 (Authenticatie en autorisatie) & ADR 003 (Data ownership): Deze POC valideert de keuze voor een centrale authenticatieservice met JWT-tokens, zoals beschreven in ADR 005. Daarnaast toont het aan dat gebruikersdata en voortgang beheerd worden binnen een eigen dataschema, conform de data ownership-principes uit ADR 003.

Uitvoering: Nog te implementeren.

&nbsp;       Resultaat: Toon aan dat de tweede service kan verifiëren wie de gebruiker is en welke rol (Student/Admin) hij heeft, puur op basis van cryptografie, zonder netwerkverbinding met de Identity service.


# 4\. Asynchrone Voortgangsregistratie (jef)

> Valideren van de hybride communicatie (ADR 002) waarbij een ingediende flag via een message broker de voortgang bijwerkt zonder dat de gebruiker blokkeert.

&nbsp;   Architecturale link: Scalability & Availability.

Voor deze opdracht zal een Proof of Concept uitgewerkt worden die test hoe het systeem kan controleren of een gebruiker een oefening correct heeft opgelost. Het doel is om aan te tonen dat ingezonden oplossingen automatisch gevalideerd kunnen worden en dat het systeem hier correct op reageert.

Concreet zal een mechanisme ontwikkeld worden waarbij een gebruiker een flag kan indienen via een endpoint. Deze flag wordt gevalideerd door de Submission Validator, waarna het resultaat via een event wordt doorgestuurd naar de Progress Tracker om de voortgang bij te werken.

Link met ADR 002 (Communicatie tussen services) & ADR 003 (Data ownership): Deze POC demonstreert het gebruik van asynchrone communicatie tussen services (Submission Validator → Progress Tracker), zoals vastgelegd in ADR 002. Daarnaast wordt bevestigd dat elke service zijn eigen data beheert en updates ontvangt via events in plaats van directe database-toegang (ADR 003).

&nbsp;   Implementatie:

&nbsp;       Zet een kleine RabbitMQ service op in een docker-compose (voor de POC).

&nbsp;       Maak twee kleine Node.js scriptjes: SubmissionService (Producer) en ProgressTracker (Consumer).

&nbsp;       Wanneer de Producer een flag "ontvangt", stuurt hij direct een "OK" terug naar de (gesimuleerde) client, maar plaatst hij een event op de queue.

&nbsp;       De Consumer verwerkt dit event met een kunstmatige vertraging van 5 seconden.

&nbsp;       Resultaat: Toon aan dat de student direct verder kan, terwijl de database-update van de score veilig op de achtergrond gebeurt.
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
