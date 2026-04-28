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

Dit diagram bevat alle studentacties uit het use-case diagram: registreren, aanmelden, profiel of niveau instellen, challenges bekijken, challenges selecteren, een oefensessie starten, code of exploit uitvoeren, een oplossing of flag indienen en de voortgang bekijken.

## Sequence diagram van de beheerder

De beheerder krijgt een afzonderlijk sequence diagram, omdat deze actor een andere verantwoordelijkheid heeft dan de student en geen leerflow doorloopt.

![Sequence diagram beheerder](./diagrammen/sequencediagram-beheerder.png)

De beheerder meldt zich eerst aan op het platform. Daarna kan een nieuwe challenge worden aangemaakt of kan een bestaande challenge worden gewijzigd. Deze wijzigingen worden verwerkt en zichtbaar gemaakt in de challengecatalogus. Daarnaast kan de beheerder een actieve sessie beëindigen en een sandbox laten opruimen of resetten.

Ook dit diagram bevat alle beheerderacties uit het use-case diagram: aanmelden, challenge aanmaken, challenge wijzigen, sessie beëindigen en sandbox opruimen.

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

# ADR Architecturale beslissingen

## Title: ADR 001: Keuze van architecturale stijl
## Status: Proposed

## Context

Het platform laat gebruikers toe echte exploits en aanvalscode uit
te voeren in geïsoleerde oefenomgevingen. De driving characteristics
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

### Gelaagde architectuur

De gelaagde architectuur verdeelt het systeem in technische lagen
(presentatie, logica, persistentie). Deze stijl scoort goed op
eenvoud en initiële kost, maar heeft significante tekortkomingen
voor dit systeem. Fault tolerance is zeer beperkt: een crash in
één laag kan het hele systeem platleggen. Scalability is eveneens
beperkt omdat het systeem als één geheel moet worden opgeschaald.
De Sandbox Provisioner, die het meest belast wordt en het grootste
veiligheidsrisico vormt, kan niet afzonderlijk worden opgeschaald
of geïsoleerd. Domeinwijzigingen, zoals het toevoegen van een nieuw
type omgeving, zijn ingrijpend omdat ze door meerdere technische
lagen heen lopen. Deze stijl valt af.

### Microkernel

De microkernel-architectuur bestaat uit een stabiele kern en
uitbreidbare plugins. Dit is sterk voor extensibility: nieuwe
challenge-types of omgevingstypes kunnen als plugin worden
toegevoegd zonder de kern te wijzigen. De stijl scoort echter
zwak op fault tolerance en scalability om dezelfde redenen als
de gelaagde architectuur: het geheel wordt monolitisch gedeployed.
Een crash in een plugin kan de kern destabiliseren tenzij hier
expliciet voor ontworpen wordt. Voor een platform waar gebruikers
actief de grenzen van omgevingen testen is dit onvoldoende.
Deze stijl valt af.

### Modulaire monoliet

De modulaire monoliet verdeelt het systeem op basis van domein
in modules met harde grenzen. Dit verbetert de onderhoudbaarheid
en maakt het mogelijk per module te redeneren over
verantwoordelijkheden. De grenzen tussen de logische componenten
uit sectie 2 kunnen hier direct worden toegepast. De stijl is
haalbaar voor een team van vier binnen zes maanden. Het
fundamentele probleem blijft echter dat het systeem als één
eenheid gedeployed wordt. De Sandbox Provisioner, die omgevingen
moet kunnen herstellen zonder andere componenten te onderbreken,
kan niet onafhankelijk worden uitgerold of opgeschaald. Security-
incidenten in een sandbox kunnen zich in theorie uitbreiden naar
andere modules omdat ze hetzelfde proces delen. Dit is voor dit
specifieke systeem een te groot risico.

### Microservices

De microservices-architectuur verdeelt het systeem in afzonderlijk
deploybare diensten op basis van domein. Elke logische component
uit sectie 2 kan als een aparte service worden uitgerold. Dit
biedt de sterkste ondersteuning voor de drie driving
characteristics. Security: de Sandbox Provisioner draait in
volledig geïsoleerde containers en een incident aldaar bereikt
andere services niet. Fault tolerance: een gecrashe sandbox-
omgeving brengt enkel de betrokken service in de problemen, de
rest van het systeem blijft operationeel. Scalability: de Sandbox
Provisioner en Challenge Interface, die het zwaarst belast worden,
kunnen onafhankelijk worden opgeschaald zonder de andere services
aan te raken. De kostprijs is reële complexiteit: gedistribueerde
systemen vereisen aandacht voor netwerkcommunicatie, data
ownership en observability.

## Decision

**We kiezen voor microservices.**

De drie driving characteristics security, fault tolerance en
scalability vereisen elk dat de Sandbox Provisioner volledig
geïsoleerd en onafhankelijk kan opereren. Geen enkele monolitische
stijl kan dit garanderen. Microservices is de enige stijl uit de
cursus die dit structureel mogelijk maakt. De hogere complexiteit
is voor dit systeem geen optionele afweging maar een noodzakelijke
kost die voortvloeit uit de aard van het platform.

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
- De Sandbox Provisioner kan onafhankelijk worden opgeschaald
- Een incident in een sandbox bereikt andere services niet
- Elke service kan afzonderlijk worden uitgerold en getest
- Services kunnen per domein in de meest geschikte technologie
  worden geïmplementeerd indien gewenst

**Wat wordt moeilijker of vereist extra werk:**
- Data ownership moet expliciet worden vastgelegd per service
- Communicatie tussen services vereist een bewuste keuze
  (synchroon of asynchroon)
- Observability over meerdere services vereist tooling
- Gedistribueerde transacties zijn complexer dan lokale

## Governance

Bij elke nieuwe feature wordt gecontroleerd of de service-grenzen
gerespecteerd worden: geen directe database-toegang over
service-grenzen heen. Dit wordt bewaakt via code review. Elke
nieuwe service vereist een bijkomende ADR die de
verantwoordelijkheid en de communicatie-interfaces vastlegt.

## Notes

**Tweede keuze: Modulaire monoliet.** De logische componenten uit
sectie 2 zijn al op basis van domein afgebakend, wat rechtstreeks
aansluit bij de domeinpartitionering van een modulaire monoliet.
Bij een kleinere teamgrootte of een strikter budget zou de
modulaire monoliet de voorkeur krijgen omdat de operationele
complexiteit significant lager is en een latere migratie naar
microservices vanuit een modulaire monoliet een gekende en
haalbare weg is.

## Title: ADR 002: Communicatie tussen services
## Status: Proposed

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

**We gebruiken synchrone communicatie (REST over HTTP) voor
tijdskritische interacties en asynchrone communicatie via een
message broker voor events waarbij de aanroeper niet hoeft
te wachten op verwerking.**

Concreet:
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
- Services zijn niet geblokkeerd op trage of falende
  ontvangers bij asynchrone communicatie
- Tijdskritische interacties blijven snel en voorspelbaar
- De Progress Tracker kan tijdelijk offline zijn zonder
  dat een indiening verloren gaat

**Wat extra werk vereist:**
- Er moet infrastructuur voorzien worden voor een message
  broker
- Asynchrone flows zijn moeilijker te debuggen dan
  synchrone calls
- Eventual consistency moet bewust worden aanvaard voor
  de Progress Tracker

## Governance

Bij elke nieuwe communicatielijn tussen services wordt in
code review gecontroleerd of de keuze synchroon/asynchroon
gemotiveerd is. Nieuwe asynchrone verbindingen worden
gedocumenteerd in een berichtenoverzicht.

## Notes

Tekst

## Title: ADR 003: Data ownership per service
## Status: Proposed

## Context

In een microservices-architectuur is het verleidelijk om één
centrale databank te delen tussen alle services. Dit vereenvoudigt
queries en vermijdt dubbele data, maar introduceert een sterke
koppeling: een schemawijziging in de gedeelde databank kan alle
services die dit schema gebruiken breken.

De logische componenten uit sectie 2 hebben elk een duidelijk
afgebakend domein. De vraag is of ze een gedeelde databank
gebruiken of elk hun eigen schema beheren.

## Decision

**Elke service beheert zijn eigen dataschema. Geen enkele service
leest rechtstreeks uit het schema van een andere service.**

Concreet betekent dit:
- User Management beheert het gebruikersschema
- Challenge Catalog beheert de challenge-metadata
- Sandbox Provisioner beheert de staat van actieve omgevingen
- Submission Validator beheert de ingediende antwoorden
- Progress Tracker beheert scores en voortgang per gebruiker
- Content Manager beheert de ruwe challenge-definities

Data die meerdere services nodig hebben wordt uitgewisseld
via de communicatiekanalen uit ADR 002, niet via gedeelde
tabellen. Dit mogen wel schema's zijn op dezelfde fysieke
databaseserver zolang de toegang via de service-API verloopt.

Als het budget groter zou zijn, zou elke service zijn eigen
fysieke database-instantie krijgen. Met het huidige team en
budget zijn gescheiden schema's op één server een aanvaardbaar
compromis.

## Consequences

**Wat wordt mogelijk:**
- Een service kan zijn schema wijzigen zonder andere services
  te breken
- Services zijn onafhankelijk testbaar en deploybaar
- Data ownership is expliciet en traceerbaar

**Wat extra werk vereist:**
- Geen JOIN-queries over service-grenzen: composities
  moeten in code worden gedaan
- Mogelijke duplicatie van data (bv. gebruikersnaam zichtbaar
  in Progress Tracker zonder rechtstreekse join op
  User Management)
- Eventual consistency bij asynchrone updates

## Governance

Code review controleert dat geen enkele service rechtstreeks
een tabel van een andere service aanroept. Dit wordt ook
bewaakt via netwerkconfiguratie: services krijgen enkel
toegang tot hun eigen schema.

## Notes

Tekst

## Title: ADR 004: Isolatie van sandbox-omgevingen
## Status: Proposed

## Context

Gebruikers voeren echte exploits en aanvalscode uit op het
platform. De Sandbox Provisioner moet garanderen dat een
gebruiker nooit buiten zijn eigen omgeving kan geraken. Dit
is de meest kritische architecturale beslissing voor de
driving characteristic security.

Er zijn drie mogelijke benaderingen:
- **Procesisolatie**: de omgeving draait als een apart proces
  op de host, geïsoleerd via OS-mechanismen
- **Containerisolatie**: de omgeving draait in een Linux
  container (Docker of gelijkaardig)
- **VM-isolatie**: de omgeving draait in een volledige
  virtuele machine

## Decision

**Sandbox-omgevingen worden geïsoleerd via Docker containers,
aangestuurd door de Sandbox Provisioner.**

Containers bieden een aanvaardbaar evenwicht tussen
isolatieniveau, snelheid van opstarten en beheersbaarheid
voor een team van vier. Een container start in seconden op,
wat de gebruikerservaring ten goede komt. De container-grenzen
voorkomen dat een gebruiker processen of bestanden van andere
gebruikers bereikt.

Containers worden uitgevoerd met minimale rechten: geen
privileged mode, beperkt CPU en geheugen, geen toegang tot
het hostnetwerk buiten de voorziene kanalen. Elke gebruikers-
sessie krijgt een verse container die na afloop vernietigd
wordt.

Als het budget groter zou zijn, zou VM-isolatie (of een
combinatie van VM's met containers erbinnen, zoals Firecracker)
de voorkeur krijgen omdat de isolatiegaranties sterker zijn.
Bij een kleiner team en budget is containerisolatie met
strikte configuratie de meest haalbare keuze.

## Consequences

**Wat wordt mogelijk:**
- Elke gebruikerssessie is volledig geïsoleerd
- Omgevingen starten snel op (seconden, geen minuten)
- De Sandbox Provisioner kan containers dynamisch aanmaken
  en vernietigen
- Resourcelimieten zijn per container instelbaar

**Wat extra werk vereist:**
- Strikte Docker-configuratie is vereist: dit is geen
  standaardinstallatie
- Container escapes zijn een reëel risico als de configuratie
  niet correct is: dit vereist security-review
- Het hostbesturingssysteem moet gehard worden

## Governance

Elke aanpassing aan de container-configuratie van de Sandbox
Provisioner vereist expliciete goedkeuring via code review.
De configuratie wordt bijgehouden in versiebeheer. Er worden
geen privileged containers toegestaan zonder een nieuwe ADR.

## Notes

Tekst

## Title: ADR 005: Authenticatie en autorisatie
## Status: Proposed

## Context

Het platform heeft meerdere soorten gebruikers met verschillende
rechten: studenten kunnen challenges uitvoeren, instructors
kunnen content aanmaken, beheerders beheren het platform.
Elke service moet weten wie een request doet en of die persoon
de gevraagde actie mag uitvoeren.

Er zijn twee benaderingen:
- **Gedistribueerd**: elke service valideert tokens en beheert
  rechten zelfstandig
- **Centraal**: één dedicated service handelt authenticatie af
  en geeft tokens uit die andere services kunnen verifiëren

## Decision

**We voorzien een centrale authenticatieservice die tokens
uitgeeft via een standaard mechanisme (JWT). Elke service
valideert binnenkomende tokens zelfstandig aan de hand van
een gedeelde publieke sleutel, zonder de centrale service
opnieuw te contacteren.**

Dit is een hybride aanpak: de uitgifte van tokens is
gecentraliseerd in User Management, de validatie is
gedistribueerd. Dit vermijdt dat elke request door een
centrale service moet passeren, wat een single point of
failure zou creëren.

Rollen worden opgenomen in het token. Een service beslist
zelf of de rol in het token voldoende is voor de gevraagde
actie.

Als het team groter of het budget hoger zou zijn, zou een
dedicated identity provider (zoals Keycloak) worden ingezet
in plaats van een zelfgebouwde authenticatieservice. Met het
huidige team is een eenvoudige JWT-gebaseerde implementatie
haalbaar en onderhoudbaar.

## Consequences

**Wat wordt mogelijk:**
- Geen single point of failure voor authenticatie bij elke
  request
- Services zijn onafhankelijk van de beschikbaarheid van
  de authenticatieservice na het uitgifte van een token
- Rollen zijn direct leesbaar uit het token zonder extra
  database-call

**Wat extra werk vereist:**
- Token-expiratie en refresh-logica moeten correct worden
  geïmplementeerd
- Het intrekken van tokens vóór expiratie is complex
  (geen centrale validatie meer)
- Elke service moet de publieke sleutel kennen en updaten
  bij rotatie

## Governance

Tokenvalidatie wordt niet gedupliceerd per service maar
geïmplementeerd als gedeelde bibliotheek. Wijzigingen aan
het tokenformaat of de sleutelrotatie vereisen coördinatie
over alle services en een nieuwe ADR.

## Notes

Security is de eerste driving characteristic uit sectie 1.
Authenticatie en autorisatie zijn de meest directe
architecturale uitwerking van die karakteristiek op
service-niveau.

# C4-diagrammen

De diagrammen zijn opgesteld volgens het C4-model en gegenereerd
via Structurizr. De broncode hieronder is de enige bron van
waarheid voor de diagrammen. De geëxporteerde PNG's zijn
opgenomen via relatieve paden.

## Broncode

```structurizr
workspace "HackLab" "Leerplatform voor hacking via uitvoerbare voorbeelden" {

    model {

        # Externe actoren
        student = person "Student" "Leert hacken via uitvoerbare challenges op het platform."
        instructor = person "Instructor" "Maakt challenges aan en publiceert deze op het platform."

        # Extern systeem
        emailProvider = softwareSystem "E-mail provider" "Verstuurt notificaties naar gebruikers bij behaalde resultaten." "External"

        # Het systeem zelf
        hacklab = softwareSystem "HackLab" "Laat gebruikers toe te leren hacken via uitvoerbare, geïsoleerde oefenomgevingen." {

            # Containers
            webApp = container "Web Application" "Levert de gebruikersinterface aan de browser." "React" "Web"

            apiGateway = container "API Gateway" "Enkel toegangspunt voor externe clients. Handelt authenticatie en routing af." "Node.js"

            userManagement = container "User Management Service" "Beheert gebruikersregistratie, aanmelden en rollen. Geeft JWT-tokens uit." "Node.js"

            challengeCatalog = container "Challenge Catalog Service" "Beheert metadata van challenges en leerpaden." "Node.js"

            contentManager = container "Content Manager Service" "Laat instructors toe challenges aan te maken en te publiceren." "Node.js"

            sandboxProvisioner = container "Sandbox Provisioner Service" "Start, stopt en monitort geïsoleerde container-omgevingen per gebruikerssessie." "Python"

            challengeInterface = container "Challenge Interface Service" "Beheert de terminal- of browsersessie van een gebruiker in een actieve sandbox." "Node.js"

            submissionValidator = container "Submission Validator Service" "Valideert ingediende flags en antwoorden." "Node.js"

            progressTracker = container "Progress Tracker Service" "Bewaart scores, voortgang en achievements per gebruiker." "Node.js"

            messageBroker = container "Message Broker" "Verzorgt asynchrone communicatie tussen services." "RabbitMQ" "Queue"

            # Databases
            userDb = container "User Database" "Bewaart gebruikersdata en tokens." "PostgreSQL" "Database"
            catalogDb = container "Catalog Database" "Bewaart challenge-metadata." "PostgreSQL" "Database"
            contentDb = container "Content Database" "Bewaart challenge-definities." "PostgreSQL" "Database"
            sandboxDb = container "Sandbox Database" "Bewaart staat van actieve omgevingen." "PostgreSQL" "Database"
            submissionDb = container "Submission Database" "Bewaart ingediende antwoorden." "PostgreSQL" "Database"
            progressDb = container "Progress Database" "Bewaart scores en voortgang." "PostgreSQL" "Database"

            # Sandbox omgevingen
            sandboxRuntime = container "Sandbox Runtime" "Geïsoleerde Docker containers waarin gebruikers hun exploits uitvoeren." "Docker" "Sandbox"
        }

        # Relaties: externe actoren met systeem
        student -> hacklab "Maakt gebruik van"
        instructor -> hacklab "Beheert challenges via"
        hacklab -> emailProvider "Verstuurt notificaties via"

        # Relaties: actoren met containers
        student -> webApp "Gebruikt via browser" "HTTPS"
        instructor -> webApp "Gebruikt via browser" "HTTPS"
        webApp -> apiGateway "Stuurt requests naar" "HTTPS/REST"

        # Relaties: API Gateway naar services (synchroon)
        apiGateway -> userManagement "Authenticeert gebruiker via" "REST"
        apiGateway -> challengeCatalog "Vraagt challenges op via" "REST"
        apiGateway -> sandboxProvisioner "Start omgeving op via" "REST"
        apiGateway -> challengeInterface "Verbindt gebruiker met sandbox via" "REST"
        apiGateway -> submissionValidator "Stuurt indiening door via" "REST"
        apiGateway -> progressTracker "Vraagt voortgang op via" "REST"
        apiGateway -> contentManager "Stuurt challenge-aanmaak door via" "REST"

        # Relaties: services naar databases
        userManagement -> userDb "Leest en schrijft" "SQL"
        challengeCatalog -> catalogDb "Leest en schrijft" "SQL"
        contentManager -> contentDb "Leest en schrijft" "SQL"
        sandboxProvisioner -> sandboxDb "Leest en schrijft" "SQL"
        submissionValidator -> submissionDb "Leest en schrijft" "SQL"
        progressTracker -> progressDb "Leest en schrijft" "SQL"

        # Relaties: asynchroon via message broker
        submissionValidator -> messageBroker "Publiceert validatieresultaat" "AMQP"
        messageBroker -> progressTracker "Levert validatieresultaat af" "AMQP"
        contentManager -> messageBroker "Publiceert nieuwe challenge" "AMQP"
        messageBroker -> challengeCatalog "Levert nieuwe challenge af" "AMQP"
        sandboxProvisioner -> messageBroker "Publiceert omgevingsevents" "AMQP"

        # Relaties: sandbox
        sandboxProvisioner -> sandboxRuntime "Start en vernietigt containers" "Docker API"
        challengeInterface -> sandboxRuntime "Beheert sessie in" "WebSocket"

        # Relaties: extern
        progressTracker -> emailProvider "Stuurt notificatie via" "HTTPS"

        # Deployment
        deploymentEnvironment "Production" {

            deploymentNode "Docker Swarm Cluster" "Testcluster met drie managers en twee workers." "Docker Swarm" {

                deploymentNode "Manager Node 1" "Swarm manager — beheert de cluster." "Ubuntu 24.04" {
                    deploymentNode "API Gateway Container" "" "Docker" {
                        containerInstance apiGateway
                    }
                    deploymentNode "User Management Container" "" "Docker" {
                        containerInstance userManagement
                    }
                    deploymentNode "Challenge Catalog Container" "" "Docker" {
                        containerInstance challengeCatalog
                    }
                }

                deploymentNode "Manager Node 2" "Swarm manager." "Ubuntu 24.04" {
                    deploymentNode "Content Manager Container" "" "Docker" {
                        containerInstance contentManager
                    }
                    deploymentNode "Submission Validator Container" "" "Docker" {
                        containerInstance submissionValidator
                    }
                    deploymentNode "Progress Tracker Container" "" "Docker" {
                        containerInstance progressTracker
                    }
                }

                deploymentNode "Manager Node 3" "Swarm manager." "Ubuntu 24.04" {
                    deploymentNode "Message Broker Container" "" "Docker" {
                        containerInstance messageBroker
                    }
                    deploymentNode "Web Application Container" "" "Docker" {
                        containerInstance webApp
                    }
                }

                deploymentNode "Worker Node 1" "Swarm worker — draait sandbox-omgevingen." "Ubuntu 24.04" {
                    deploymentNode "Sandbox Provisioner Container" "" "Docker" {
                        containerInstance sandboxProvisioner
                    }
                    deploymentNode "Challenge Interface Container" "" "Docker" {
                        containerInstance challengeInterface
                    }
                    deploymentNode "Sandbox Runtime Containers" "Dynamisch aangemaakte containers per gebruikerssessie." "Docker" {
                        containerInstance sandboxRuntime
                    }
                }

                deploymentNode "Worker Node 2" "Swarm worker — draait databases." "Ubuntu 24.04" {
                    deploymentNode "User DB" "" "Docker" {
                        containerInstance userDb
                    }
                    deploymentNode "Catalog DB" "" "Docker" {
                        containerInstance catalogDb
                    }
                    deploymentNode "Content DB" "" "Docker" {
                        containerInstance contentDb
                    }
                    deploymentNode "Sandbox DB" "" "Docker" {
                        containerInstance sandboxDb
                    }
                    deploymentNode "Submission DB" "" "Docker" {
                        containerInstance submissionDb
                    }
                    deploymentNode "Progress DB" "" "Docker" {
                        containerInstance progressDb
                    }
                }
            }
        }
    }

    views {

        systemContext hacklab "SystemContext" {
            include *
            autolayout lr
            title "Systeemcontextdiagram — HackLab"
        }

        container hacklab "Containers" {
            include *
            autolayout lr
            title "Containerdiagram — HackLab"
        }

        deployment hacklab "Production" "Deployment" {
            include *
            autolayout lr
            title "Deployment diagram — HackLab (Docker Swarm)"
        }

        styles {
            element "Person" {
                shape Person
                background #1168bd
                color #ffffff
            }
            element "Software System" {
                background #1168bd
                color #ffffff
            }
            element "External" {
                background #999999
                color #ffffff
            }
            element "Container" {
                background #438dd5
                color #ffffff
            }
            element "Database" {
                shape Cylinder
                background #438dd5
                color #ffffff
            }
            element "Queue" {
                shape Pipe
                background #438dd5
                color #ffffff
            }
            element "Web" {
                shape WebBrowser
                background #438dd5
                color #ffffff
            }
            element "Sandbox" {
                background #e03030
                color #ffffff
            }
        }
    }
}
```

## Systeemcontextdiagram

![Systeemcontextdiagram](./diagrammen/c4-context.png)

Het systeemcontextdiagram toont de twee gebruikerstypen, Student
en Instructor en hun relatie met het HackLab-systeem als geheel.
Een externe e-mailprovider wordt aangesproken voor notificaties.

## Containerdiagram

![Containerdiagram](./diagrammen/c4-container.png)

Het containerdiagram toont de afzonderlijk deploybare services,
hun onderlinge communicatie en de databanken die elk beheren.
De API Gateway is het enige synchrone toegangspunt voor de
Web Application. Asynchrone communicatie verloopt via de
Message Broker. De Sandbox Runtime is rood gemarkeerd omdat
deze de veiligheidsgrens van het systeem vormt.

## Deployment diagram

![Deployment diagram](./diagrammen/c4-deployment.png)

Het deployment diagram toont de verdeling over de Docker Swarm
testcluster van drie managers en twee workers. Worker Node 1
draait uitsluitend de sandbox-gerelateerde containers omdat
deze het zwaarst belast worden en de grootste veiligheidsrisico's
vormen. Worker Node 2 draait uitsluitend de databases.

