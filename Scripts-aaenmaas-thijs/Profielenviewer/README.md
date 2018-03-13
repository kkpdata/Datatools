# Inleiding
De profielenviewer is een GUI om dwarsprofielen te visusaliseren. De opmaak voor de input van de profielenviewer is dezelfde als de input voor DAM Edit Design.

Als voorbeeid zijn twee CSV-bestanden bijgevoegd, *voorbeeldinput_1.csv* en *voorbeeldinput_2.csv*.

## Vereisten
* Python 2.7

# Input
Als input wordt eenzelfde CSV-document gebruikt als voor de invoer van DAM Edit Design, ook wel bekend als de klik-tool. De viewer gebruikt binnen dit bestand de volgende kolommen: `X`, `Y`, `Z` en `DIJKPAAL`. `CODE` en `SUBCODE` zijn irrelevant en mogen ongevuld zijn zolang X, Y, Z en DIJKPAAL maar in kolom C t/m F (3 t/m 6) staan.

Eisen aan het importdocument:
* CSV-formaat (; als lijstscheidingsteken)
* Per profiel moeten de profielpunten opeenvolgend gedefinieerd worden
* Begin- en eindpunten van de profielen moeten gedefinieerd zijn en eenzelfde afstand hebben. De profielen worden over elkaar geplot dus het vergelijken van een profiel van 100m en 200m werkt niet. Wel mogen tussen het begin en eindpunt de afstand tussen de punten en de hoeveelheid punten variabel zijn.

## Opmerkingen:
* De assen zijn nog ietwat hard gedefinieerd, dit moet nog aangepast worden.
* De viewer is toegestpitst op Aa en Maas, maar met kleine aanpassingen kan het ook bij andere waterschappen gebruikt worden.

# Voorbeeld
![Voorbeeld profielenviewer](https://github.com/kkpdata/Datatools/blob/master/Scripts-aaenmaas-thijs/Profielenviewer/voorbeeld.png "Profielenviewer")

