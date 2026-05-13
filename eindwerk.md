# Karakteristieken

De klant wil een platform waarop gebruikers kunnen leren hacken via
uitvoerbare voorbeelden, vergelijkbaar met TryHackMe. Gebruikers
voeren dus effectief code en exploits uit binnen het systeem. Op
basis hiervan worden de volgende zeven karakteristieken als
belangrijkst beschouwd.

## Security 

Gebruikers voeren echte exploits en aanvalscode uit op het platform.
Een zwakke isolatie tussen oefenomgevingen kan ertoe leiden dat een
gebruiker buiten zijn sandbox geraakt en andere gebruikers, het
platform zelf of de onderliggende infrastructuur schaadt. Security
is bijgevolg de meest kritische karakteristiek van dit systeem: het
is geen optionele toevoeging maar een fundamentele randvoorwaarde
waaraan elk onderdeel van de architectuur moet voldoen.

## Fault Tolerance 

Elke gebruiker werkt in een eigen uitvoerbare omgeving. Als één
oefenomgeving crasht, vastloopt of door een gebruiker opzettelijk
gesaboteerd wordt, mag dit geen invloed hebben op de omgevingen van
andere gebruikers of op de werking van het platform zelf. Fault
tolerance is hier dus niet alleen een kwaliteitskenmerk maar ook een
rechtstreeks gevolg van de aard van het systeem: gebruikers testen
actief de grenzen van omgevingen.

## Scalability 

Een leerplatform voor hacking trekt een breed publiek aan. Elke
actieve gebruiker heeft een eigen geïsoleerde omgeving nodig die
rekenkracht en geheugen verbruikt. Het systeem moet bijgevolg kunnen
meeschalen met het aantal gelijktijdige gebruikers zonder dat de
kwaliteit van de omgevingen achteruitgaat.

## Availability

Gebruikers plannen leersessies en verwachten dat het platform
beschikbaar is wanneer ze het nodig hebben. Uitval van het platform
onderbreekt actieve oefensessies en beschadigt het vertrouwen van
gebruikers. Volledige hoge beschikbaarheid is binnen het budget van
een half jaar met een team van vier niet haalbaar op het niveau van
een grote cloudprovider, maar de architecturale keuzes mogen de
beschikbaarheid niet onnodig beperken.

## Extensibility

De waarde van een hackingplatform zit grotendeels in de breedte en
actualiteit van het aanbod aan uitdagingen. Nieuwe kwetsbaarheden,
technieken en technologieën moeten als nieuwe modules of uitdagingen
aan het systeem kunnen worden toegevoegd zonder dat de kern van het
systeem hiervoor aangepast of heruitgerold moet worden.

## Elasticity

Het gebruik van het platform zal niet constant zijn. Bij het
uitbrengen van nieuwe inhoud, bij georganiseerde CTF-events
(Capture The Flag) of bij schoolperiodes zullen er pieken zijn in
het aantal actieve gebruikers. Het systeem moet tijdelijk kunnen
opschalen en daarna terug afschalen om kosten te beheersen.

## Configurability

Gebruikers hebben uiteenlopende achtergronden en doelstellingen.
Een beginner heeft nood aan begeleide oefeningen met hints, terwijl
een gevorderde gebruiker direct aan complexe scenario's wil werken.
Het systeem moet dit onderscheid kunnen maken en gebruikers in staat
stellen hun eigen leerpad samen te stellen.

# Logische componenten

Het online hackingplatform wordt in deze sectie opgesplitst in logische componenten. Die componenten beschrijven de functionele bouwblokken van het systeem en hun verantwoordelijkheden. Het gaat hier nog niet om services, containers of deployment-eenheden, maar om een logische opdeling van het systeem.

## Tijdlijn van de gebruikersflow

Als vertrekpunt wordt eerst de typische flow van een student bekeken bij het oplossen van een hacking challenge. Die tijdlijn maakt zichtbaar welke stappen doorlopen worden en welke verantwoordelijkheden daaruit voortvloeien.

![Workflowdiagram](./diagrammen/workflow.png)

De flow start wanneer een student zich aanmeldt op het platform. Daarna worden challenges doorzocht en wordt een challenge geselecteerd. Vervolgens wordt een oefenomgeving opgestart en maakt de student verbinding met de sandbox. In die omgeving voert de student commando's, scripts of exploits uit. Daarna wordt een oplossing of flag ingediend, waarna het resultaat wordt teruggegeven en de student zijn voortgang en score kan bekijken.

Deze tijdlijn toont dat de functionaliteit van het systeem uit meerdere duidelijk verschillende taken bestaat. Authenticatie, profielbeheer, challengebeheer, sessiebeheer, sandbox-uitvoering en evaluatie hebben elk een eigen rol binnen het platform.

## Use-case diagram

Het use-case diagram geeft op hoofdlijnen weer welke interacties de student en de beheerder met het platform hebben.

![Use-case diagram](./diagrammen/usecasediagram.png)

De student gebruikt het platform om zich te registreren of aan te melden, zijn profiel of niveau in te stellen, challenges te bekijken en te selecteren, een oefensessie te starten, code of exploits uit te voeren, een oplossing of flag in te dienen en nadien de voortgang te bekijken.

De beheerder gebruikt het platform om zich aan te melden, challenges aan te maken en te wijzigen, sessies te beëindigen en sandboxen op te ruimen.

Het use-case diagram toont enkel de interacties tussen de actoren en het platform. De interne afhandeling van die acties wordt verder uitgewerkt in de sequence diagrammen.

## Sequence diagram van de student

De interacties van de student worden afzonderlijk weergegeven zodat de volledige leerflow in één samenhangend diagram zichtbaar blijft.

![Sequence diagram student](./diagrammen/sequencediagram-student.png)

In deze flow registreert en authenticatieert de student zich eerst via het platform. Daarna worden profiel en niveau ingesteld. Vervolgens vraagt de student het challenge-overzicht op, selecteert een challenge en start een oefensessie. Het platform laat daarvoor een sandbox klaarzetten. Tijdens de sessie voert de student code of exploits uit en dient daarna een oplossing of flag in. Ten slotte wordt de oplossing gevalideerd, de voortgang bijgewerkt en de geactualiseerde voortgang opnieuw aan de student getoond.

## Sequence diagram van de beheerder

De beheerder krijgt een afzonderlijk sequence diagram, omdat deze actor een andere verantwoordelijkheid heeft dan de student en geen leerflow doorloopt.

![Sequence diagram beheerder](./diagrammen/sequencediagram-beheerder.png)

De beheerder meldt zich eerst aan op het platform. Daarna kan een nieuwe challenge worden aangemaakt of kan een bestaande challenge worden gewijzigd. Deze wijzigingen worden verwerkt en zichtbaar gemaakt in de challengecatalogus. Daarnaast kan de beheerder een actieve sessie beëindigen en een sandbox laten opruimen of resetten.

## Afleiding van de logische componenten

Uit de tijdlijn, het use-case diagram en de sequence diagrammen volgen de logische componenten van het platform. Elke component groepeert taken die inhoudelijk bij elkaar horen en een gezamenlijke verantwoordelijkheid vormen.

### Identity & Access

Deze component behandelt registratie, authenticatie, sessiebeheer en toegangscontrole. Alle interacties rond het identificeren van studenten en beheerders worden hier samengebracht.

### Profile & Learning Path

Deze component beheert profielinformatie, niveau-instellingen, voortgang en het persoonlijke leerpad van een student.

### Challenge Catalog

Deze component ontsluit het beschikbare aanbod aan challenges en levert de informatie die nodig is om challenges te bekijken en te selecteren.

### Session Orchestrator

Deze component beheert de levenscyclus van een oefensessie. Het opstarten en beëindigen van sessies wordt hier ondergebracht.

### Sandbox Runtime

Deze component levert de effectieve uitvoeromgeving waarin een student commando's, scripts en exploits uitvoert. Ook het resetten en opruimen van de omgeving behoort tot deze component.

### Evaluation & Scoring

Deze component valideert oplossingen of flags, bepaalt het resultaat van een challengepoging en ondersteunt de verwerking van feedback en voortgang.

### Content Authoring

Deze component ondersteunt het inhoudelijk beheer van challenges. Het aanmaken en wijzigen van oefenmateriaal wordt hier gegroepeerd.

## Taken per component

### Identity & Access

- Gebruikers registreren.
- Studenten en beheerders authenticeren.
- Toegangscontrole uitvoeren.
- Sessies valideren.

### Profile & Learning Path

- Profielgegevens bewaren.
- Niveau-instellingen beheren.
- Voortgang opslaan.
- Leerstatus teruggeven.

### Challenge Catalog

- Beschikbare challenges tonen.
- Geselecteerde challengegegevens teruggeven.
- De catalogus actualiseren na beheeracties.

### Session Orchestrator

- Oefensessies starten.
- Actieve sessies beëindigen.
- Sandbox-opstart aanvragen.
- Sessiestatus bewaken.

### Sandbox Runtime

- Oefenomgevingen uitvoeren.
- Code en exploits verwerken.
- Uitvoer teruggeven.
- Sandboxen resetten of opruimen.

### Evaluation & Scoring

- Oplossingen en flags valideren.
- Resultaten bepalen.
- Feedback genereren.
- Voortgangsupdates aanleveren.

### Content Authoring

- Challenges aanmaken.
- Bestaande challenges wijzigen.
- Wijzigingen opslaan.
- Inhoud beschikbaar maken voor de catalogus.

## Samenhang van de opdeling

De gekozen opdeling volgt de natuurlijke scheiding tussen toegang, leerinformatie, challengebeheer, sessiebeheer, uitvoering en evaluatie. Daardoor krijgt elke belangrijke taak van het platform een duidelijke plaats binnen het systeem.

De studentflow en de beheerderflow tonen bovendien dat inhoudelijk beheer, uitvoering van challengecode en toegangscontrole niet in éénzelfde component thuishoren. Door die verantwoordelijkheden te scheiden ontstaat een duidelijker en beter verdedigbaar logisch model van het platform.

## Van logische componenten naar containers

De logische componenten uit de vorige sectie zijn de conceptuele
bouwblokken van het systeem. In de C4-diagrammen worden deze
vertaald naar concrete, deploybare containers. De namen
verschillen bewust: de logische naam beschrijft de verantwoordelijkheid,
de containernaam beschrijft de implementatie.

| Logische component    | Container                        |
|-----------------------|----------------------------------|
| Identity & Access     | User Management Service          |
| Profile & Learning Path | Progress Tracker Service       |
| Challenge Catalog     | Challenge Catalog Service        |
| Session Orchestrator  | Sandbox Provisioner Service      |
| Sandbox Runtime       | Sandbox Runtime                  |
| Evaluation & Scoring  | Submission Validator Service     |
| Content Authoring     | Content Manager Service          |

# ADR Architecturale beslissingen

## Title: ADR 001: Keuze van architecturale stijl
### Status: Accepted

## Context

Het platform laat gebruikers toe echte exploits en aanvalscode uit
te voeren in geïsoleerde oefenomgevingen. De belangrijkste architecturale karakteristieken
zijn security, fault tolerance en scalability. Het ontwikkelteam
telt vier personen en heeft een doorlooptijd van zes maanden voor
een productieklare versie.

De vier stijlen die in overweging genomen worden zijn de stijlen
die in de cursus aan bod zijn gekomen:

| Stijl              | Partitionering | Deployment      |
|--------------------|----------------|-----------------|
| Gelaagd            | Technisch      | Monolitisch     |
| Microkernel        | Technisch      | Monolitisch     |
| Modulaire monoliet | Domein         | Monolitisch     |
| Microservices      | Domein         | Gedistribueerd  |

Elke stijl wordt geëvalueerd op basis van de impact op de belangrijkste karakteristieken.

## Decision

**We kiezen voor microservices.**

Deze keuze wordt gemaakt omdat de drie belangrijkste karakteristieken 
(security, fault tolerance en scalability) vereisen dat kritieke
onderdelen, zoals de Sandbox Provisioner, onafhankelijk
kunnen opereren, schalen en falen zonder impact op anderen delen van het systeem.

Microservices bieden deze isolatie en onafhankelijkheid structureel, 
terwijl monolitische stijlen dit niet kunnen garanderen.

Als het team groter of het budget hoger zou zijn, zou de keuze
voor microservices nog sterker worden ondersteund door de
mogelijkheid tot teamautonomie per service. Als het team kleiner
of het budget lager zou zijn, zou de modulaire monoliet de tweede
keuze zijn: de grenzen tussen de logische componenten zijn al
vastgelegd en een latere migratie naar microservices is vanaf
een modulaire monoliet haalbaarder dan vanuit een gelaagde
architectuur.

## Consequences

**Wat wordt mogelijk:**
- Services kunnen onafhankelijk worden opgeschaald (vooral Sandbox Provisioner)
- Fouten in één service beïnvloeden andere services niet
- Services kunnen afzonderlijk worden ontwikkeld, getest en gedeployed
- Mogelijkheid om per service technologiekeuzes te maken

**Wat wordt moeilijker of vereist extra werk:**
- Complexere communicatie tussen services (netwerk, latency)
- Data ownership moet expliciet worden vastgelegd
- Observability en monitoring vereisen extra tooling
- Gedistribueerde systemen verhogen de complexiteit van debugging en testing

## Governance

Bij elke nieuwe feature wordt gecontroleerd of de service-grenzen
gerespecteerd worden: geen directe database-toegang over
service-grenzen heen. Dit wordt bewaakt via code review. Elke
nieuwe service vereist een bijkomende ADR die de
verantwoordelijkheid en de communicatie-interfaces vastlegt.
Communicatiepatronen worden vastgelegd volgens ADR 002.

## Notes

**Tweede keuze: Modulaire monoliet.**
Deze stijl sluit goed aan bij de domein-gebaseerde componenten 
en is eenvoudiger te implementeren binnen een klein team.
De keuze voor microservices wordt echter gerechtvaardigd 
door de hogere eisen op vlak van security, fault tolerance 
en scalability.

## Title: ADR 002: Communicatie tussen services
### Status: Accepted

## Context

De microservices uit sectie 3 moeten met elkaar communiceren.
Er zijn twee fundamentele opties: synchrone communicatie via
HTTP/REST waarbij de aanroeper wacht op een antwoord, en
asynchrone communicatie via een message broker waarbij de
aanroeper een bericht plaatst en verder werkt zonder te wachten.

De communicatiepatronen tussen de logische componenten uit
sectie 2 zijn niet allemaal van hetzelfde type:

- Een student vraagt een challenge op uit de catalog → de UI
  wacht op een antwoord (tijdskritisch)
- Een student dient een flag in => de Submission Validator
  verwerkt dit en de Progress Tracker moet worden bijgewerkt,
  maar de student hoeft niet te wachten tot de score
  opgeslagen is om zijn resultaat te zien
- De Sandbox Provisioner meldt dat een omgeving gecrasht is
  => andere services hoeven hier niet op te wachten maar
  moeten wel verwittigd worden

## Decision

**Er wordt gekozen voor een hybride communicatiemodel:**
- **Synchrone communicatie (REST over HTTP)** voor tijdskritische 
interacties waarbij een onmiddelijk antwoord vereist is
- **Asynchrone communicatie (via een message broker)** voor events 
waarbij de aanroeper niet hoeft te wachten op verwerking

Concrete toepassing:
- Student <=> Challenge Catalog: synchroon
- Student <=> Sandbox Provisioner (opstarten): synchroon
- Student <=> Challenge Interface: synchroon
- Submission Validator => Progress Tracker: asynchroon
- Sandbox Provisioner => andere services (crash, stop): asynchroon
- Content Manager => Challenge Catalog (publicatie): asynchroon

Als het team groter of het budget hoger zou zijn, zou een
API gateway als enkel synchrone toegangspoort voor externe
clients worden toegevoegd, wat authenticatie en rate limiting
centraliseert. Bij een kleiner team zou volledig synchrone
communicatie eenvoudiger te beheren zijn, maar dit gaat ten
koste van fault tolerance.

## Consequences

**Wat wordt mogelijk:**
- Services zijn minder afhankelijk van elkaar bij 
asynchrone communicatie
- Tijdskritische interacties blijven snel en voorspelbaar
- Het systeem is beter bestand tegen tijdelijke uitval van services
- Verwerking kan schaalbaar gebeuren via event-based flows

**Wat extra werk vereist:**
- Infrastructuur voor een message broker moet voorzien worden
- Asynchrone flows zijn moeilijker te debuggen en te testen
- Eventual consistency moet expliciet aanvaard worden
- Complexiteit in foutafhandeling en retries

## Governance

Bij elke nieuwe communicatielijn tussen services wordt in
code review gecontroleerd of de keuze synchroon/asynchroon
gemotiveerd is. Nieuwe asynchrone verbindingen worden
gedocumenteerd in een berichtenoverzicht. Nieuwe messaging-patronen vereisen 
een bijkomende ADR indien ze impact hebben op meerdere services.

## Notes

Deze beslissing ondersteunt de karakteristieken **fault tolerance** en **scalability**, 
zoals gedefinieerd in sectie 1. Als het team groter of het budget hoger zou zijn, 
kan een API gateway toegevoegd worden als centrale toegangspoort voor externe clients. 
Dit zou authenticatie, logging en rate limiting centraliseren. 
Bij een kleiner team of eenvoudiger systeem zou een volledig synchrone aanpak 
eenvoudiger zijn, maar dit gaat ten koste van robuustheid en schaalbaarheid.

## Title: ADR 003: Data ownership per service
### Status: Accepted

## Context

Binnen een microservices-architectuur moeten services omgaan 
met dataopslag. Een mogelijke aanpak is het gebruik van één 
gedeelde databank voor alle services. Dit vereenvoudigt queries 
en vermijdt dataduplicatie, maar introduceert sterke koppeling 
tussen services: wijzigingen aan het databankschema kunnen 
meerdere services tegelijk breken.

De logische componenten in dit systeem zijn duidelijk afgebakend 
per domein (bijv. gebruikersbeheer, challenges, voortgang). Dit 
roept de vraag op of deze componenten een gedeelde databank moeten 
gebruiken of elk hun eigen dataschema moeten beheren.

Daarnaast vereisen de karakteristieken **scalability, fault tolerance 
en maintainability** dat services zo onafhankelijk mogelijk 
kunnen evolueren en deployen.

## Decision

Elke service beheert zijn **eigen dataschema**. Geen enkele service
leest of schrijft rechtstreeks naar het schema van een ander service.

Data-uitwisseling tussen services gebeurt uitsluitend via de 
communicatiekanalen zoals gedefinieerd in ADR 002, en niet 
via gedeelde databanktables.

Concreet betekent dit:
- User Management beheert het gebruikersschema
- Challenge Catalog beheert de challenge-metadata
- Submission Validator beheert de ingediende antwoorden
- Progress Tracker beheert scores en voortgang per gebruiker
- Content Manager beheert de ruwe challenge-definities

Als implementatiekeuze worden deze schema's ondergebracht op 
één fysieke databaseserver, met strikte scheiding per service.
Toegang tot data verloopt uitsluitend via de respectieve service-API.

## Consequences

**Wat wordt mogelijk:**
- Services kunnen onafhankelijk evolueren zonder impact op andere services
- Services zijn onafhankelijk testbaar en deploybaar
- Data ownership is expliciet en duidelijk per domein
- Schemawijzigingen zijn lokaal en beheersbaar

**Wat extra werk vereist:**
- JOIN-queries over servicegrenzen zijn niet mogelijk
- Data moet soms gedupliceerd worden tussen services
- Eventual consistency moet aanvaard worden bij asynchrone updates
- Composities van data moeten in applicatielogica gebeuren

## Governance

Code review controleert dat geen enkele service rechtstreeks
een tabel van een andere service aanroept. Dit wordt ook
bewaakt via netwerkconfiguratie: services krijgen enkel
toegang tot hun eigen schema. Nieuwe data-afhankelijkheden 
moeten via API's of events verlopen. Wijzigingen in datastructuren 
worden gedocumenteerd en kunnen aanleiding geven tot een nieuwe ADR.

## Notes

Deze beslissing ondersteunt de karakteristieken **scalability, 
fault tolerance en maintainability** door sterke koppeling 
tussen services te vermijden. Bij een groter budget of complexer 
systeem zou elke service een eigen fysieke database-instantie krijgen. 
In de huidige context (team van vier, beperkte scope) is een 
gedeelde databaseserver met gescheiden schema’s een pragmatisch compromis.

## Title: ADR 004: Isolatie van sandbox-omgevingen
### Status: Accepted


## Context

Gebruikers van het platform voeren echte exploits en aanvalscode 
uit binnen oefeningomgevingen. Dit brengt een hoog veiligheidsrisico 
met zich mee: een onvoldoende geïsoleerde omgeving kan leiden 
tot toegang tot andere gebruikersomgevingen of tot de onderliggende 
infrastructuur.

De isolatie van sandbox-omgevingen is daarom een kritische 
architecturale beslissing die rechtstreeks impact heeft op 
de karakteristieken **security** en **fault tolerance**.

Er zijn drie mogelijke benaderingen voor isolatie:
- **Procesisolatie**: uitvoering als aparte processen op de 
host, geïsoleerd via OS-mechanismen
- **Containerisolatie**: uitvoering binnen containers (bijv. Docker)
- **VM-isolatie**: uitvoering binnen volledige virtuele machines

Elke benadering biedt een verschillend niveau van isolatie, 
performantie en operationele complexiteit.

## Decision

**Sandbox-omgevingen worden geïsoleerd via containerisolatie (Docker),
aangestuurd door de Sandbox Provisioner.**

Deze keuze wordt gemaakt omdat containerisolatie een evenwicht biedt tussen:
- voldoende sterke isolatie voor het uirvoeren van onbetrouwbare code
- snelle opstarttijden (seconden in plaats van minuten)
- beheersbaarheid binnen de beperkingen van een klein team

Elke gebruikssessie krijgt een tijdelijke, geïsoleerde container 
die na gebruik automatisch wordt beëindigd en verwijderd.

Containers worden uitgevoerd met minimale rechten:
- geen privileged mode
- beperkte CPU- en geheugentoewijzing
- gecontroleerde netwerktoegang
- geen directe toegang tot host resources

## Consequences

**Wat wordt mogelijk:**
- Gebruikersomgevingen zijn logisch en technisch geïsoleerd van elkaar
- Omgevingen kunnen snel en dynamisch worden opgestart
- De Sandbox Provisioner kan omgevingen automatisch beheren (start/stop/herstel)
- Resourcegebruik kan per container gecontroleerd worden

**Wat extra werk vereist:**
- Containerisolatie biedt minder sterke garanties dan volledige VM-isolatie
- Foute configuratie kan leiden tot container escapes
- Extra aandacht vereist voor beveiliging van de hostomgeving
- Security-configuratie vraagt expliciete validatie en testing

## Governance

Elke aanpassing aan de container-configuratie van de Sandbox
Provisioner vereist expliciete goedkeuring via code review.
De configuratie wordt bijgehouden in versiebeheer. Er worden
geen privileged containers toegestaan zonder een nieuwe ADR.
Security-instellingen worden expliciet getest binnen POC 1 (Container Isolation).

## Notes

Deze beslissing ondersteunt primair de karakteristiek security, 
en in tweede instantie fault tolerance doordat falende 
of gecompromitteerde omgevingen geïsoleerd blijven.
Bij een groter budget of strengere security-eisen zou 
VM-gebaseerde isolatie (bijv. Firecracker) overwogen worden 
om sterkere isolatiegaranties te bieden. De haalbaarheid 
van deze keuze wordt gevalideerd in POC 1.

## Title: ADR 005: Authenticatie en autorisatie
### Status: Accepted 

## Context

Het platform ondersteunt meerdere types gebruikers met verschillende 
rechten, zoals studenten, instructors en beheerders. Elke 
service moet kunnen bepalen wie een request uitvoert en of deze 
gebruiker gemachtigd is om de gevraagde actie uit te voeren.

Binnen een microservices-architectuur zijn er twee mogelijke benaderingen:
- **Gedistribueerde aanpak**: elke service beheert authenticatie en 
  autorisatie zelfstandig
- **Centrale aanpak**: één service verzorgt authenticatie en
  geeft tokens uit die door andere services gevalideerd worden

De keuze moet rekening houden met de karakteristieken security, 
scalability en availability, en moet vermijden dat een centrale 
component een bottleneck of single point of failure wordt.

## Decision

Er wordt gekozen voor een **hybride aanpak**:
- Een centrale authenticatieservice (User Management) verzorgt de uitgifte van tokens
- Elke service valideert tokens lokaal zonder de authenticatieservice 
  opnieuw te contacteren

Authenticatie gebeurt via JWT. Tokens bevatten gebruikersinformatie 
en rollen, en worden ondertekend met een private sleutel. Services 
valideren tokens aan de hand van de bijhorende publieke sleutel.

Autorisatie gebeurt op basis van rollen die in het token zijn opgenomen. 
Elke service bepaalt zelf of een gebruiker voldoende rechten heeft 
voor een bepaalde actie.

Deze aanpak combineert centrale controle over identiteit met 
gedistribueerde validatie, waardoor afhankelijkheid van één 
service tijdens runtime wordt vermeden.

## Consequences

**Wat wordt mogelijk:**
- Geen centrale bottleneck of SPF bij elke request
- Services blijven operationeel zonder directe afhankelijkheid
  van de authenticatieservice
- Authenticatie-informatie is direct beschikbaar in het token
- Schaalbaarheid wordt ondersteund doordat validatie lokaal gebeurt

**Wat extra werk vereist:**
- Token-expiratie en refresh-mechanismen moeten correct 
  worden geïmplementeerd
- Intrekken van tokens voor expiratie is complex
- Sleutelbeheer vereist coördinatie
- Elke service moet correct omgaan met tokenvalidatie en autorisatie

## Governance

Tokenvalidatie wordt niet gedupliceerd per service maar
geïmplementeerd als gedeelde bibliotheek. Wijzigingen aan
het tokenformaat of de sleutelrotatie vereisen coördinatie
over alle services en een nieuwe ADR. Code reviews controleren 
correcte implementatie van authenticatie en autorisatie.

## Notes

Deze beslissing ondersteunt primair de karakteristiek security, 
en draagt bij aan scalability en availability door het 
vermijden van een centrale afhankelijkheid tijdens runtime.

Bij een groter team of complexere omgeving zou een externe 
identity provider (bijv. Keycloak) overwogen worden om 
authenticatie en autorisatie verder te standaardiseren.

De haalbaarheid van deze beslissing wordt gevalideerd in POC 3 (Authentication & User Progress).

# C4-diagrammen

De diagrammen zijn opgesteld volgens het C4-model en gegenereerd
via Structurizr. 

```structurizr
workspace "HackLab" "Leerplatform voor hacking via uitvoerbare voorbeelden" {

    model {

        student = person "Student" {
            description "Leert hacken via uitvoerbare, geïsoleerde challenges op het platform."
            tags "User"
        }

        instructor = person "Instructor" {
            description "Maakt challenges aan, wijzigt ze en beëindigt sessies of ruimt sandboxen op."
            tags "User"
        }

        hacklab = softwareSystem "HackLab" {
            description "Laat gebruikers toe te leren hacken via uitvoerbare, geïsoleerde oefenomgevingen."

            webApp = container "Web Application" {
                description "Levert de gebruikersinterface aan de browser voor student en instructor."
                technology "React 18, TypeScript, Vite"
                tags "Web"
            }

            apiGateway = container "API Gateway" {
                description "Enig synchroon toegangspunt. Valideert JWT lokaal, past rate limiting toe en routeert naar backend-services."
                technology "Node.js 22, Express"
                tags "Gateway"
            }

            userManagement = container "User Management Service" {
                description "Beheert registratie, aanmelden en rollen. Geeft ondertekende JWT-tokens uit."
                technology "Node.js 22, Express, bcrypt, jsonwebtoken"
                tags "Service"
            }

            challengeCatalog = container "Challenge Catalog Service" {
                description "Beheert en ontsluit metadata van beschikbare challenges en leerpaden."
                technology "Node.js 22, Express"
                tags "Service"
            }

            contentManager = container "Content Manager Service" {
                description "Laat de instructor toe challenges aan te maken en te wijzigen."
                technology "Node.js 22, Express"
                tags "Service"
            }

            sandboxProvisioner = container "Sandbox Provisioner Service" {
                description "Start, monitort en vernietigt geïsoleerde Docker-containers per sessie."
                technology "Python 3.12, Docker SDK"
                tags "Service"
            }

            challengeInterface = container "Challenge Interface Service" {
                description "Proxiet de terminalsessie tussen browser en sandbox-container."
                technology "Node.js 22, xterm.js, WebSocket"
                tags "Service"
            }

            submissionValidator = container "Submission Validator Service" {
                description "Valideert ingediende flags en publiceert het resultaat asynchroon."
                technology "Node.js 22, Express"
                tags "Service"
            }

            progressTracker = container "Progress Tracker Service" {
                description "Bewaart scores en voortgang. Ontvangt validatieresultaten asynchroon."
                technology "Node.js 22, Express"
                tags "Service"
            }

            messageBroker = container "Message Broker" {
                description "Asynchrone event-bus tussen services (ADR 002)."
                technology "RabbitMQ 3.13"
                tags "Queue"
            }

            userDb = container "User Database" {
                description "Eigendom van User Management Service."
                technology "PostgreSQL 16"
                tags "Database"
            }

            catalogDb = container "Catalog Database" {
                description "Eigendom van Challenge Catalog Service."
                technology "PostgreSQL 16"
                tags "Database"
            }

            contentDb = container "Content Database" {
                description "Eigendom van Content Manager Service."
                technology "PostgreSQL 16"
                tags "Database"
            }

            sandboxDb = container "Sandbox Database" {
                description "Eigendom van Sandbox Provisioner Service."
                technology "PostgreSQL 16"
                tags "Database"
            }

            submissionDb = container "Submission Database" {
                description "Eigendom van Submission Validator Service."
                technology "PostgreSQL 16"
                tags "Database"
            }

            progressDb = container "Progress Database" {
                description "Eigendom van Progress Tracker Service."
                technology "PostgreSQL 16"
                tags "Database"
            }

            sandboxRuntime = container "Sandbox Runtime" {
                description "Geïsoleerde containers per sessie. Geen netwerktoegang tot het platform. Alleen bereikbaar door Sandbox Provisioner en Challenge Interface."
                technology "Docker, seccomp + AppArmor, internal overlay network"
                tags "Sandbox"
            }

            webApp             -> apiGateway          "Stuurt alle API-verzoeken naar"                "HTTPS / REST"
            apiGateway         -> userManagement       "Registratie en aanmelden via"                 "REST"
            apiGateway         -> challengeCatalog     "Challenge-overzicht en -detail via"           "REST"
            apiGateway         -> sandboxProvisioner   "Sessie starten en beëindigen via"             "REST"
            apiGateway         -> challengeInterface   "Terminalsessie verbinden via"                 "REST / WebSocket"
            apiGateway         -> submissionValidator  "Flag indienen via"                            "REST"
            apiGateway         -> progressTracker      "Voortgang opvragen via"                       "REST"
            apiGateway         -> contentManager       "Challenge aanmaken of wijzigen via"           "REST"
            userManagement     -> userDb               "Leest en schrijft"                            "SQL"
            challengeCatalog   -> catalogDb            "Leest en schrijft"                            "SQL"
            contentManager     -> contentDb            "Leest en schrijft"                            "SQL"
            sandboxProvisioner -> sandboxDb            "Leest en schrijft"                            "SQL"
            submissionValidator -> submissionDb        "Leest en schrijft"                            "SQL"
            progressTracker    -> progressDb           "Leest en schrijft"                            "SQL"
            submissionValidator -> messageBroker       "Publiceert validatieresultaat"                "AMQP"
            messageBroker      -> progressTracker      "Levert validatieresultaat af"                 "AMQP"
            contentManager     -> messageBroker        "Publiceert challenge-update"                  "AMQP"
            messageBroker      -> challengeCatalog     "Levert challenge-update af"                   "AMQP"
            sandboxProvisioner -> messageBroker        "Publiceert sandbox-events"                    "AMQP"
            sandboxProvisioner -> sandboxRuntime       "Start en vernietigt containers via"           "Docker API"
            challengeInterface -> sandboxRuntime       "Proxiet I/O naar en van"                      "WebSocket"
        }

        student    -> hacklab "Leert hacken via"
        instructor -> hacklab "Beheert challenges en sessies via"
        student    -> webApp  "Opent platform via browser"          "HTTPS"
        instructor -> webApp  "Beheert challenges via browser"      "HTTPS"

        deploymentEnvironment "Production" {

            deploymentNode "Docker Swarm Cluster" {
                description "Vijf nodes: drie identieke managers voor Raft-consensus en hoge beschikbaarheid, twee workers exclusief voor sandbox-containers."
                technology "Docker Swarm mode, Ubuntu 24.04 LTS"
                tags "Cluster"

                # ── Managers: identiek, Swarm verdeelt de workload ────────────
                # Alle platform-services draaien als Swarm services met
                # replica's verdeeld over de drie managers.
                # Bij uitval van één manager herplaatst Swarm de containers
                # automatisch op de overige twee.

                deploymentNode "Manager Nodes (×3)" {
                    description "Drie identieke manager nodes. Draaien samen de Raft-consensus engine. De Swarm scheduler verdeelt alle platform-services automatisch over deze drie nodes. Bij uitval van één manager herplaatst Swarm de betrokken containers op de overige managers."
                    technology "Ubuntu 24.04 LTS, Docker Engine 27"
                    tags "ManagerNode"
                    instances 3

                    deploymentNode "Platform Services" {
                        description "Alle platform-services draaien als Swarm services met placement constraint node.role==manager. Replica's worden automatisch verdeeld."
                        technology "Docker Swarm services"

                        containerInstance webApp {
                            description "2 replica's, verdeeld over de drie managers door de Swarm scheduler."
                        }
                        containerInstance apiGateway {
                            description "2 replica's, verdeeld over de drie managers."
                        }
                        containerInstance userManagement {
                            description "1 replica, door Swarm geplaatst op een beschikbare manager."
                        }
                        containerInstance challengeCatalog {
                            description "1 replica."
                        }
                        containerInstance contentManager {
                            description "1 replica."
                        }
                        containerInstance submissionValidator {
                            description "1 replica."
                        }
                        containerInstance progressTracker {
                            description "1 replica."
                        }
                        containerInstance challengeInterface {
                            description "1 replica."
                        }
                        containerInstance sandboxProvisioner {
                            description "1 replica, met toegang tot Docker socket voor sandbox-beheer."
                        }
                        containerInstance messageBroker {
                            description "1 replica, named volume rabbitmq-data voor persistentie."
                        }
                    }

                    deploymentNode "Databases" {
                        description "Alle databases draaien als Swarm services met placement constraint op manager nodes. Named volumes garanderen persistentie."
                        technology "Docker Swarm services, named volumes"

                        containerInstance userDb {
                            description "Named volume: user-db-data"
                        }
                        containerInstance catalogDb {
                            description "Named volume: catalog-db-data"
                        }
                        containerInstance contentDb {
                            description "Named volume: content-db-data"
                        }
                        containerInstance sandboxDb {
                            description "Named volume: sandbox-db-data"
                        }
                        containerInstance submissionDb {
                            description "Named volume: submission-db-data"
                        }
                        containerInstance progressDb {
                            description "Named volume: progress-db-data"
                        }
                    }
                }

                # ── Workers: exclusief voor sandbox-containers (ADR 004) ───────
                # Sandbox-containers krijgen een placement constraint
                # node.role==worker zodat ze NOOIT op een manager terechtkomen.
                # Dit is de enige bewuste scheiding in de Swarm-topologie
                # en vloeit rechtstreeks voort uit ADR 004.

                deploymentNode "Worker Nodes (×2)" {
                    description "Twee identieke worker nodes exclusief voor sandbox-containers. Placement constraint node.role==worker zorgt dat sandbox-containers hier terechtkomen en nooit op de managers. Bij uitval van één worker herplaatst Swarm actieve sandboxen op de andere worker."
                    technology "Ubuntu 24.04 LTS, Docker Engine 27"
                    tags "WorkerNode"
                    instances 2

                    deploymentNode "Sandbox Containers" {
                        description "Dynamisch aangemaakte containers per gebruikerssessie. Draaien in isolated_lab_net, een intern overlay-netwerk zonder egress naar platform-services of internet."
                        technology "Docker, internal overlay network, seccomp + AppArmor"

                        containerInstance sandboxRuntime {
                            description "Per-sessie container, automatisch vernietigd na afsluiten."
                        }
                    }
                }
            }
        }
    }

    views {

        systemContext hacklab "SystemContext" {
            title "Systeemcontextdiagram — HackLab (C4 Niveau 1)"
            include *
            autolayout lr 300 150
        }

        container hacklab "Containers" {
            title "Containerdiagram — HackLab (C4 Niveau 2)"
            include *
            autolayout lr 250 100
        }

        deployment hacklab "Production" "Deployment" {
            title "Deployment diagram — HackLab (C4 Niveau 3, Docker Swarm)"
            include *
            autolayout lr 300 150
        }

        styles {
            element "Person" {
                shape Person
                background #1168bd
                color #ffffff
                fontSize 14
            }
            element "Software System" {
                background #1168bd
                color #ffffff
                fontSize 14
            }
            element "Web" {
                shape WebBrowser
                background #438dd5
                color #ffffff
            }
            element "Gateway" {
                shape Hexagon
                background #2e6da4
                color #ffffff
            }
            element "Service" {
                background #438dd5
                color #ffffff
            }
            element "Queue" {
                shape Pipe
                background #e6a118
                color #ffffff
            }
            element "Database" {
                shape Cylinder
                background #438dd5
                color #ffffff
            }
            element "Sandbox" {
                background #e03030
                color #ffffff
                border Dashed
            }
            element "ManagerNode" {
                background #0c3d6e
                color #ffffff
            }
            element "WorkerNode" {
                background #7a1f1f
                color #ffffff
            }
            element "Cluster" {
                background #e8f0f8
                color #1a1a1a
                border Dashed
            }
        }

        theme default
    }
}
```


## Systeemcontextdiagram

![Systeemcontextdiagram](./diagrammen/systeemcontextdiagram_2.png)

Het systeemcontextdiagram toont de twee gebruikerstypen, Student
en Instructor en hun relatie met het HackLab-systeem als geheel.


## Containerdiagram

![Containerdiagram](./diagrammen/d3Containers.png)

Het containerdiagram toont de afzonderlijk deploybare services,
hun onderlinge communicatie en de databanken die elk beheren.
De API Gateway is het enige synchrone toegangspunt voor de
Web Application. Asynchrone communicatie verloopt via de Message Broker.

**Legende:**
- Volle lijn: synchrone communicatie (REST)
- Stippellijn: asynchrone communicatie (AMQP via Message Broker)
- Blauw: services en databases
- Oranje: Message Broker (asynchrone event-bus)
- Rood: Sandbox Runtime (geïsoleerde uitvoeringsomgeving voor onbetrouwbare code)
- Zeshoek: API Gateway (enkel extern toegangspunt)

## Deployment diagram

![Deployment diagram](./diagrammen/d3Deployment.png)

Het deployment diagram toont hoe de containers uit niveau 2 fysiek worden ingezet op de concrete Docker Swarm-infrastructuur.

# Proofs of Concept

## POC 1 — Container Isolation
Valideert ADR 004. Toont aan dat Docker-containers als geïsoleerde 
sandbox kunnen dienen: geen privileged mode, beperkte resources, 
automatische opruiming na gebruik.
Zie README.md in de poc directory.

## POC 2 — Sandbox Failure Recovery
Valideert ADR 001 en ADR 004. Toont aan dat een crash in één sandbox 
beperkt blijft en dat de Sandbox Provisioner dit detecteert en herstelt, 
zonder impact op andere actieve sandboxen.
Zie README.md in de poc directory.

## POC 3 — Distributed JWT Validation
Valideert ADR 005. Toont aan dat JWT-tokens centraal uitgegeven worden 
(RS256, private key) en gedistribueerd gevalideerd worden (public key), 
zonder runtime-afhankelijkheid van de centrale service.
Zie README.md in de poc directory.

## POC 4 — Asynchrone Voortgangsregistratie
Valideert ADR 002 en ADR 003. Toont aan dat een flag-indiening asynchroon 
verwerkt wordt via RabbitMQ: de student krijgt direct feedback, terwijl de 
Progress Tracker op de achtergrond bijgewerkt wordt, ook bij tijdelijke uitval.
Zie README.md in de poc directory.
