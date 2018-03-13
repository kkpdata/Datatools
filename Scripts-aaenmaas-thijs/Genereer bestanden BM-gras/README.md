# Inleiding
Binnen het toetsspoor GABU wordt BM Grasbekledingen gebruikt om de erosiebestendigheid van het buitentalud te berekenen. Per vak dienen, per beoordeelde faalkanscategorie, individuele berekeningen te worden uitgevoerd wat resulteert in veel verschillende projectbestanden, veelal handmatig ingevuld. Om dit proces te vergemakkelijk en om fouten in invoer te voorkomen is dit script opgezet.

Dit script genereert, op basis van input in een Excelbestand, reeds ingevulde GRSX-projectbestanden **voor het deelmechanisme golfklap, in het bovenrivierengebied**. Oploopberekeningen of berekeningen met een afwijkende Q-variant zouden met enkele eenvoudige aanpassingen aan het script toegevoegd kunnen worden. Tevens is een script bijgevoegd om de resultaten automatisch uit te lezen.

## Scripts
* `maak_BM-gras.py`: genereer GRSX-bestanden
* `lees_BM-gras.py`: lees veiligheidsfactoren uit

## Vereisten
* Python 3.6

# Input
De input-Exceldocumenten bevatten alle relevante parameters ten behoeve van de beoordeling. Dit zijn onder andere de in Ringtoets berekende hydraulische belastingen en de sterkteparameters. De kolombenamingen zijn overeenstemmig met de terminologie in de Ringtoets SQL-database die ten grondslag ligt aan de projectbestanden.

* `Name`: naam van het projectbestand [-]
* `ZGrassMin`: ondergrens van de grasbekleding (golfklapzone) [m+NAP]
* `ZGrassMax`: bovengrens van de grasbekleding (golfklapzone) [m+NAP]
* `ZswlMin`: ondergrens waterstand [m+NAP]
* `ZswlMax`: bovengrens waterstand [m+NAP]
* `Hour1`: begin stormopzetduur [u]
* `Hour2`: einde stormopzetduur [u]
* `Zswl1`: taludhoogte horende bij maximaal voorkomende golfhoogte [m+NAP]
* `Qws1`: taludhoogte horende bij maximaal voorkomende golfhoogte [m+NAP]
* `Qws2`: taludhoogte horende bij maximaal voorkomende golfhoogte, -0.01 [m+NAP]
* `QHm0`: maximaal voorkomende golfhoogte [m+NAP]
* `DeltaZ`: verticale stapgrootte [m]
* `Hm0Min`: minimale significante golfhoogte [m]
* `Hm0Max`: maximale significante golfhoogte [m]
* `ConstantA`: sterkteparameter [m]
* `ConstantB`: sterkteparameter [1/u]
* `ConstantC`: sterkteparameter [m]
* `Dcombined`: Dikte kleilaag + gras [m]
* `Fsand`: zandgehalte

*Ten behoeve van de berekening in BM Grasbekledingen wordt `Qws2` gedefinieerd als 1 cm onder de taludhoogte horende bij de maximaal voorkomende golfhoogte.*