# projectopdracht ICT Architecture
Je krijgt een korte omschrijving van een vraag van een klant. Deze vraag is heel beknopt en laat grote
delen van de opdracht open. Als groep formuleer je een plausibel antwoord op deze open vragen en
werk je een architectuur uit, waarbij je rekening houdt met belangrijke functionaliteit en gewenste
karakteristieken. Je voorziet de gevraagde analysedocumenten en proofs-of-concept van je
voorgestelde oplossingen voor de grootste uitdagingen.
De vraag van de klant varieert naargelang je groep. Je krijgt deze apart toegestuurd per mail.
Je schrijft je opdracht uit in CommonMark Markdown. Afbeeldingen,... moeten via relatieve paden
vermeld worden in de tekst, losse bestanden worden niet bekeken.
Het is niet verboden AI te raadplegen, maar je draagt zelf de eindverantwoordelijkheid. Tijdens de
verdediging moet elk groepslid het project kunnen verdedigen. Als iemand in je groep niet mee is, moet
je die persoon mee krijgen. Als het eindresultaat technisch sterk is, maar de helft van de groep het niet
kan verdedigen, is dat geen goed resultaat.
Indien je alles helemaal volgens de regels van de kunst afwerkt zonder extra's en je verdediging goed
loopt, behaal je als groepscijfer 16/20.
# karakteristieken
Maak een lijst van de 7 belangrijkste karakteristieken van je applicatie. Licht toe waarom deze zo
belangrijk zijn voor dit probleem in een paar zinnen per karakteristiek.
# logische componenten
Leg, volgens de actor-action en/of workflow approach, logische componenten vast voor je applicatie.
Geef daarna een uitdrukkelijk overzicht van de taken van elke component. Denk eraan: componenten
zijn geen "services". Ze worden bepaald voor je een stijl gekozen hebt.
# ADR architecturale stijl
Stel een ADR op waarin je de gekozen architecturale stijl verantwoordt. Je mag dit doen volgens de
template uit de les of volgens een standaardformaat, op voorwaarde dat je een referentie naar dat
formaat toevoegt. Je moet alle stijlen die in de les aan bod zijn gekomen in overweging nemen, ook de
stijlen die nog niet behandeld zijn wanneer deze opdracht is vrijgegeven. In je ADR maak je ook
duidelijk welke stijl je tweede keuze zou zijn en waarom.
# verdere beslissingen
Stel nog (aantal groepsleden) bijkomende ADR's op voor wat jij beschouwt als de "belangrijkste"
beslissingen. Met andere woorden, de belangrijkste knopen om door te hakken.
# diagrammen
Stel, volgens het C4-model, diagrammen op die matchen met de eerdere keuzes die je gemaakt hebt.
Je voorziet een systeemcontextdiagram, een containerdiagram en een deployment diagram. Gebruik
hiervoor Structurizr en voeg de broncode toe in een Markdown code block binnen je hoofddocument.
# proofs of concept
Werk, voor wat je beschouwt als de (aantal groepsleden) meest uitdagende aspecten, aparte proofs of
concept uit. Deze moeten uiteraard compatibel zijn met de beslissingen uit je ADR's. Het mogen losse,
kleine programma's zijn. Het is niet de bedoeling dat je één volledige applicatie maakt. Integendeel,
heel uitgewerkte frontends, enorme bergen metrics, supergedetailleerde config files... zorgen alleen
voor ruis en dat is een slechte zaak. Als je echt enthousiast bent over je applicatie, kan je die dingen
voor jezelf uitwerken.
Bij wijze van voorbeeld: beschouw het labo rond microkernels als een "proof of concept" van hoe je een
monolitisch pluginsysteem zou implementeren. Je mag dat labo overigens niet indienen als je eigen
proof of concept (indien je toevallig een pluginsysteem in C♯ wil gebruiken), maar een vertaling naar
een andere programmeertaal zou wel mogen. Hoe duidelijker je POC een technische vraag
beantwoordt, hoe beter.
De POC's zijn niet ingebed in de Markdown. Per POC maak je een directory in je inzending. Elke POC
moet opgestart kunnen worden door naar die directory te navigeren en dan docker stack deploy -f
poc.yaml poc uit te voeren. De testcluster telt drie managers en twee workers. Dit wil niet zeggen dat
elke POC een service met replica's is of dat er een web interface moet zijn. Het kan ook zijn dat de
gebruiker docker exec -it ... moet doen op de node(s) waarop de POC uitvoert. Licht toe in een
README.md per POC.
# extra's
Het is toegelaten dat je wat verder gaat dan de vragen hierboven. Misschien is er een andere
architecturale stijl die je geschikter lijkt dan de stijlen uit de les, een interessant architecturaal patroon,
een nuttige tool die we niet in de les behandeld hebben,... Die zaken mag je toevoegen in de meest
relevante sectie van je einddocument. Je doet dat dan expliciet in een subsectie "uitbreiding" (één extra
hoofdingsniveau in Markdown). In dat geval vermeld je ook een goede bron, bijvoorbeeld een goede vrij
te raadplegen paper, artikel of website over het onderwerp.
Chats met een LLM zijn geen goede bron, maar ook Medium posts vol bullet lists, boeken van auteurs
die wekelijks publiceren,... zijn niet degelijk. En er bestaan ook slechte artikels die door mensen
geschreven zijn. Het belangrijkste: als je een bron gebruikt, betekent dat dat je hele groep deze
onderschrijft.
# verdediging
Voor de verdediging wordt een planner voorzien. Tijdens de verdediging wordt de volledige groep
verwacht. Het is de verantwoordelijkheid van de hele groep dat ieder groepslid op vragen over het hele
document (inclusief de code voor de POC's) kan antwoorden.
Indien iemand uit de groep tijdens de laatste weken op internationale week is, krijgt die groep voorrang
voor de resterende week. In geval van gewettigde afwezigheid van een groepslid gaat de verdediging
door met de andere groepsleden en moeten de afwezigen achteraf alleen verdedigen via een
Teamsgesprek in de examenperiode.
