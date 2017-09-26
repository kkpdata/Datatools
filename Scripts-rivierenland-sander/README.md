# Inleiding
In 2015 en 2016 heeft Co Drost in opdracht van Waterschap Rivierenland python scripts ontwikkeld om GEF-files in te lezen in een file geodatabase binnen ArcGis. Deze scripts worden 'as is' beschikbaar gesteld, zonder enige vorm van ondersteuning. 

## Doel
Het doel van deze scrips is om de metadata en de data uit de GEF-files op een uniforme manier te structureren en iets met deze data te kunnen doen. Het datamodel is zelf ontworpen en sluit gedeeltelijk aan bij landelijke standaarden.

## Gebruik
De toolbox (GEF10.2.tbx) is in te laden in ArcGis. Het is getest met ArcGis versie 10.2.2. De python scripts en toolbox moeten in de zelfde map staan.
Let er op dat je de GEF files van boringen en sonderingen van elkaar scheidt. Het script herkent niet of de GEF file een boring is of een sondering.

## Functionaliteit per script
"importGEF" leest de GEFs in en maakt indien nodig de juiste features aan.
"KoppelGrndSoort" berekent de terreinspanningen op basis van een gekoppelde tabel met laagscheidingen. Dit werkt echter niet foutloos. In de testset is een voorbeeldtabel toegevoegd.
"exportCSV" exporteert per sondering/boring de data in sondering_lagen en boring_lagen

## bekende Issues
Het script "KoppelGrndSoort" is niet foutloos. Bij meerdere sonderingen ontstaat een rijverschil waardoor terreinspanningen niet goed berekend worden.

## Contact
Co Drost - [Giswerk](https://www.giswerk.nl/)
Sander Kapinga - [Waterschap Rivierenland](https://www.waterschaprivierenland.nl/)
