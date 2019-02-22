*Profielenviewer v2.0*

**Veranderingen ten opzichte van de oude profielenviewer:**
* Gebruikt Python 3.6
* Opent zowel de input voor DAM Edit Design als qDAMEdit
* Meer GUI-functionaliteiten (Zoom, pan, opslaan, legenda)
* [executable](https://github.com/kkpdata/Datatools/releases/tag/Profielenviewer) beschikbaar

# Inleiding
De profielenviewer is een GUI om dwarsprofielen te visusaliseren. 

Als voorbeeid zijn twee CSV-bestanden bijgevoegd, *voorbeeld_oud_formaat.csv* en *voorbeeld_nieuw_formaat.csv*.
 
## Vereisten
* Python 3.6 (Of gebruik de [executable](https://github.com/kkpdata/Datatools/releases/tag/Profielenviewer))

# Input
Als input wordt eenzelfde CSV-document gebruikt als voor de invoer van DAM Edit Design of qDamEdit, ook wel bekend als de klik-tools. Voorbeelden van beide bestanden zijn meegeleverd.

Eisen aan het importdocument:
* CSV-formaat (; als lijstscheidingsteken)
* Per profiel moeten de profielpunten opeenvolgend gedefinieerd worden
* Begin- en eindpunten van de profielen moeten gedefinieerd zijn en eenzelfde afstand hebben. De profielen worden over elkaar geplot dus het vergelijken van een profiel van 100m en 200m werkt niet. Wel mogen tussen het begin en eindpunt de afstand tussen de punten en de hoeveelheid punten variabel zijn.

## Opmerkingen:
* De viewer is toegestpitst op de dataformats zoals ze bij Aa en Maas gehanteerd worden, maar met kleine aanpassingen kan het ook bij andere waterschappen gebruikt worden.

# Voorbeeld
![Voorbeeld profielenviewer](https://github.com/kkpdata/Datatools/blob/master/Scripts-aaenmaas-thijs/Profielenviewer%202/voorbeeld.png "Profielenviewer")
