# Inleiding
WBI Tools ontwikkeld voor het toetsproces, specifiek voor de situatie binnen het werkgebied van Waterschap Rijn en IJssel. 

## Doel
Genereren profielen voor de toetsporen STPH(1_Surfacelines) en GEKB(2_PRFLprofielen) en het structureren van het gehele proces van vakken bepalen, reken invoer maken en verwerken van resultaten.

## Gebruik
De Toolbox is gemaakt met ArcGIS versie 10.5.1. <br>
Met FME is de basisdata gegenereerd en klaar gezet.(WS Friesland tools) Output zie: Ringtoets_WRIJ48_1.gdb<br>
Beschrijving FME modellen zie: [FME_modellen_uitvoer_volgorde_prflTool.pdf](https://github.com/kkpdata/Datatools/blob/master/Scripts-rijnenijssel-edwin/documentatie/FME_modellen_uitvoer_volgorde_prflTool.pdf)<br>
De scripts zijn gemaakt met python 2.7.

## Beschrijving tools
Sommige scripts zijn specifiek voor WRIJ en worden niet beschreven.<br>
Gaat hier om bijvoorbeeld het aanmaken van vaknamen of het selecteren van data uit het beheerregister.<br>
In de scripts zijn sommige parameters of rekenmogelijkheden van Riskeer niet meegenomen of hebben een vaste waarde gekregen, omdat ze binnen het werkgebied van WRIJ niet voorkomen of niet wijzigen.

De toolbox bestaat uit 5 toolsets en welke hier kort worden beschreven.

![Toolbox v2](https://github.com/kkpdata/Datatools/blob/master/Scripts-rijnenijssel-edwin/tbx2.png "Toolbox v2")

<b>0_Datavoorbereiding</b>
Dit zijn enkele specifieke WRIJ tools. <br>
Het uitlezen van de HRD locaties leest een *.rtd uit met daarin 2x hetzelfde traject, 1x doorgerekend met de signaleringswaarde en 1x met de ondergrens.<br>
Het resultaat is een gis bestand met de berekende waterstanden en golfhoogtes.

<b>1_Surfacelines</b>
Scripts voor het toetsspoor Piping.<br>
Globaal maakt de tool een bestand aan van het traject met de benodigde kolommen, welke als basis dient voor de vervolgstappen.<br>
* per vak een representatief profiel selecteren
* csv en shp voor Riskeer wegschrijven
* bepalen snijpunt piping in- en uittredelijn
* XML met de berekening wegschrijven(direct gekoppeld met *.soil) 
* variant door obv de mediaan het representatieve profiel te bepalen
Gedetailleerde uitleg in: <br>
[20181009_Handleiding_SurfacelinesTool_Piping_Macro_v2_ENIE.pdf](https://github.com/kkpdata/Datatools/blob/master/Scripts-rijnenijssel-edwin/documentatie/20181009_Handleiding_SurfacelinesTool_Piping_Macro_v2_ENIE.PDF)

<b>2_PRFLprofielen</b>
Scripts voor het toetsspoor Hoogte.<br>
Globaal maakt de tool een bestand aan van het traject met de benodigde kolommen, welke als basis dient voor de vervolgstappen.<br>
* taludhelling bepalen tbv het verfijnen van de vakindeling
* profielen per vak selecteren en bekijken
* prfl punten inklikken en uittekenen profiellijn
* prfl's, shape en XML met de berekening wegschrijven
* voor de langscontructies prfl en mappenstructuur tbv HYDRA-NL aanmaken
Gedetailleerde uitleg in:<br>
[20181009_Handleiding_HoogteTool_v2_ENIE.pdf](https://github.com/kkpdata/Datatools/blob/master/Scripts-rijnenijssel-edwin/documentatie/20181009_Handleiding_HoogteTool_v2_ENIE.PDF)

<b>3_Riskeer_resultaten_verwerken</b>
Uitlezen berekend Riskeer project naar één overzichtelijke tabel met de belangrijkste resultaten.

<b>4_Rapportage</b>
Enkele tools om de data makkelijk te visualiseren. Onder andere door gebruik te maken van data driven pages<br>
of per soil segment de bijbehorende vakken te exporteren.

## Contact
Gert de Jonge [www.wrij.nl]<br>
Emiel Huizinga [www.wrij.nl]<br>
Edwin Nieuwland [www.witteveenbos.com]
