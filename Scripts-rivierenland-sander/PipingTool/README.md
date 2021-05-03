# PipingTool

In deze repository is de PipingTool opgenomen. De PipingTool is een tool in ArcMap waarmee op basis van een alternatieve, aangescherpte methode het risico op het faalmechanisme piping bepaald kan worden. De tool volgt dezelfde veiligheidsbenadering als het Wettelijk Beoordelingsinstrumentarium (WBI2017) en het OntwerpInstrumentarium OI2014v4 maar biedt aanscherpingen op verschillende onderdelen. De tool is alleen toepasbaar binnen het geldigheidsbereid van de rekenregel van Sellmeijer zoals beschreven in onderzoeksrapport zandmeevoerende wellen.

Zo worden geen dijkvakken in een 2D dwarsdoorsnede getoetst maar potentiele uittredepunten. Het uittredepunt is te beschouwen als een mogelijke locatie voor een (zandmeevoerende) wel. Voor ieder uittredepunt wordt door de PipingTool automatisch de kortste afstand naar bijvoorbeeld de intredelijn bepaald. Met de tool kunnen vrij gemakkelijk veel uittredepunten doorgerekend worden. Door de veelvoud aan berekende uittredepunten ontstaat een gebiedsdekkend beeld van het risico op piping.

## Ondersteuning
De PipingTool is ontwikkeld in samenwerking tussen Waterschap Rivierenland en Royal HaskoningDHV. De tool is in verschillende projecten succesvol toegepast en is 'as-is' vrij te gebruiken. Ondersteuning bij het gebruik van de PipingTool is alleen mogelijk op projectbasis. 
Voor ondersteuning kan contact opgenomen worden met:

* Sander Kapinga van Waterschap Rivierenland
* Tom de Wit van Royal HaskoningDHV

## Opbouw repository
* de map "01 Rapportage" bevat de hoofd en achtergrondrapportages
* de map "02 De PipingTool" bevat de benodigde python scripts en de ArcMap toolbox
* de map "03 Configuratietabel" is nodig voor de juiste configuratie van de PipingTool
* de map "04 Testdata" omvat de bestanden die gebruikt zijn in de validatie van de tool.

