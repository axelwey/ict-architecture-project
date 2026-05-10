# POC 2 – Sandbox Failure Recovery

## Doel
Het doel is aan te tonen dat:
- een crash beperkt blijft tot de betrokken sandbox
- andere actieve sandboxen operationeel blijven
- de Sandbox Provisioner de fout detecteert
- automatisch herstel of heropstart mogelijk is

Concreet worden meerdere sandboxcontainers gestart. Eén container wordt geforceerd beëindigd of in een fault-state gebracht. Vervolgens wordt gecontroleerd of:
- de andere containers bereikbaar blijven
- de crash correct wordt gedetecteerd
- een event wordt gepubliceerd
- de container automatisch vervangen kan worden

## Architecturale link

- ADR 001 (Microservices) Valideert dat falen geïsoleerd blijft.
- ADR 004 (Sandbox Isolatie) Toont dat sandbox failure containment werkt.

## Ondersteunde karakteristieken
- Fault tolerance
- Security
- Availability