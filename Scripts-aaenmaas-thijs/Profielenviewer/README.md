# Inleiding
De profielenviewer is een GUI om dwarsprofielen te visusaliseren. De opmaak voor de input van de profielenviewer is dezelfde als de input voor DAM Edit Design.

Als voorbeeid zijn twee CSV-bestanden bijgevoegd, *voorbeeldinput_1.csv* en *voorbeeldinput_2.csv*.

# Benodigde kolommen:

`CODE	SUBCODE	X	Y	Z	DIJKPAAL`
`NVT	NVT	float	float	float	string`

De viewer gebruikt de volgende kolommen: X, Y, Z en DIJKPAAL. CODE en SUBCODE zijn irrelevant en mogen leeg zijn zolang X, Y, Z en DIJKPAAL maar in kolom C t/m F (3 t/m 6) staan.

Eisen aan het importdocument:
* CSV-formaat
* Per profiel moeten de profielpunten opeenvolgend gedefinieerd worden
* Begin- en eindpunten van de profielen moeten gedefinieerd zijn en eenzelfde afstand hebben. De profielen worden over elkaar geplot dus het vergelijken van een profiel van 100m en 200m werkt niet. Wel mogen tussen het begin en eindpunt de afstand tussen de punten en de hoeveelheid punten variabel zijn.

## Opmerkingen:
Assen zijn nog hard gedefinieerd, moeten nog aangepast worden.

# Voorbeeld
![Voorbeeld profielenviewer](https://github.com/kkpdata/Datatools/blob/master/Scripts-aaenmaas-thijs/Profielenviewer/voorbeeld.png "Profielenviewer")

