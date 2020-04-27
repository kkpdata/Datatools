# Toets op maat geohydrologie en piping voor het bovenrivierengebied

Sander Kapinga, Waterschap Rivierenland

## Inleiding

Voor de bepaling van de ontwerpopgave is een alternatieve, aangescherpte methode ontwikkeld op basis van het Wettelijk Beoordelingsinstrumentarium (WBI). In deze toelichting wordt de methode van deze toets op maat toegelicht en de belangrijkste keuzes die hierbij gemaakt zijn. Binnen het WBI is dit een mogelijke uitwerking van een Toets op Maat (TOM).

De invoer is vastgelegd in verschillende tabbladen in een excel bestand. Het bijbehorende script leest deze tabellen in en koppelt uittredepunten, ondergrondschematisatie waterstandsverloop per vak. Op basis van dit gekoppelde bestand worden de berekeningen uitgevoerd. De rekenwijze is met een eerste toelichting vastgelegd in een Jupyter-notebook.

Daarnaast is een tool in ontwikkeling die deze methodiek beschikbaar maakt binnen een ArcGIS omgeving.

## Methode

Conform het WBI spelen drie deelfaalmechanismen een rol in de pipingberekening:

* opbarsten;
* heave;
* terugschrijdende erosie.

De kans op falen door piping per doorsnede is bepaald door de kleinste kans van falen door één van deze drie deelmechanismen. De aanpak van de Toet op Maat verschilt op een aantal punten van het WBI. Deze verschillen worden in deze paragraaf toegelicht.

Met deze methode worden geen dwarsdoorsneden getoetst aan piping, maar wordt uitgegaan van uittredepunten, met ieder een kortste afstand tot de intredelijn. De berekende kwelwegen hoeven niet loodrecht op de kering te lopen, maar kiezen het kortste pad naar het uittredepunt. Deze afstand is dus onafhankelijk van een dwarsprofiel over de kering. Het uittredepunt is te beschouwen als een mogelijke locatie voor een (zandmeevoerende) wel.
Elk uittredepunt is te beschouwen als een doorsnede waarbij een voor die locatie realistische combinatie van parameters wordt geschematiseerd. Door de veelvoud aan berekende kwelwegscenario’s ontstaat een gebiedsdekkend beeld van het pipingrisico. Maaiveldniveau en gebiedskenmerken zijn sturende aspecten voor de locaties van uittredepunten. Geometrische kenmerken zoals maaiveldniveau, kwelweglengte en afstand tot waterkering worden per uittredepunt vastgelegd, waardoor mogelijke combinaties van deze stochasten expliciet wordt meegenomen. Onrealistische combinaties worden hiermee uitgesloten. .

Een ander verschil is het rekenen met een zogenaamde ‘gelumpte’ weerstand in het voorland: de mate van weerstand in het voorland is onzeker en is bepalend voor de kwelweglengte in het voorland. De effectieve voorlandlengte wordt bepaald door een combinatie van geometrische factoren (fysieke aanwezige lengte) en de mate van weerstand (spreidingslengte) van het voorland. Een toelichting op de bepaling van de weerstand is opgenomen in de jupyter notebook.

Modelmatig wordt een expliciet verband gelegd tussen de geohydrologische schematisering (het potentiaalverloop) en de schematisering voor de pipingberekening. Het theoretische potentiaalverloop onder de dijk is per uittredepunt bepaald en kan indien mogelijk geijkt worden aan de beschikbare metingen. Hiervoor zijn in dit voorbeeld de modellen uit het Technisch Rapport Waterspanningen bij dijken gebruikt, maar een benadering op basis van andere grondwaterstromingsmodellen is ook mogelijk. Uit deze schematisering van de geohydrologische potentiaalverlopen volgt de respons per uittredepunt.

Vanwege de opzet is deze TOM zeer geschikt om vanuit een basisschematisatie in verschillende rekenslagen naar een uiteindelijke schematisatie te komen. De methode is zo ontworpen dat het mogelijk is om zowel op vakniveau als lokaal niveau te schematiseren. Naast de belasting geven ook lokale verschillen in geometrie en bodemopbouw (aanwezigheid van sloten, Holocene tussenzandlagen, kleine gefundeerde Holocene zandbanen) aanleiding om scherper te willen schematiseren. De top van het zand alsmede de scenariokansverdeling kan lokaal (per uittredepunt) worden aangepast. Door deze methode is het beter inzichtelijk wat de faalkans bepalende parameters zijn en kunnen kwalitatieve bronnen, zoals de zandbanenkaart expliciet worden meegenomen in de schematisatie. Door deze ruimtelijke schematisatie en doordat meerdere punten berekend worden, is beter inzichtelijk wat de maatgevende schematisatie is.

## Veiligheidsbenadering

De aangescherpte methode, zoals hierboven beschreven, hanteert dezelfde veiligheidsbenadering als het OI2014 en het WBI. De methode gaat, gelijk aan de methode van het WBI, uit van een semi-probabilistische berekening met karakteristieke waarden die door extrapolatie een benaderde faalkans per scenario levert. Deze benaderde faalkansen worden vervolgens gecombineerd met de kans op optreden van het scenario. De gecombineerde faalkans wordt getoetst aan de faalkans eis per doorsnede voor het mechanisme piping.

Bij de vertaling van de benaderde faalkans per uittredepunt naar de faalkans per vak moet rekening worden gehouden met lengte-effecten. De vakken zijn bepaald op basis van de verwachte onzekerheden in de ondergrond en geometrische kenmerken. De vakgrootte is zodanig gekozen dat zij groter of minimaal gelijk is aan de referentie-lengte voor het lengte-effect. De lengte geeft de omvang van de karakteristieke afmetingen van het (geohydrologische en piping) model, en sluit aan bij de uitgangspunten van de kalibratie. Deze aanpak volgt het advies van het KPR met betrekking tot de vakgrootte.

Per vak wordt een veelvoud van doorsnedekansen berekend. Er zijn meerdere benaderingen beschikbaar om deze doorsnedekansen op te schalen naar een vak- en trajectkans. Om aan te sluiten bij het WBI hanteert dit voorbeeld de volgende benadering. De grootste faalkans per vak geeft de bepalende (maatgevende) doorsnedekans per vak. In Riskeer wordt deze doorsnedekans gecorrigeerd met een aangenomen lengte-effect om een vakkans te berekenen.

## Ondergrondschematisatie

De ondergrondschematisatie wordt per vak vastgelegd. Binnen deze methode zijn drie hoofdscenario’s vastgesteld:

* scenario met een (dikke) deklaag: opbarsten en piping vanuit het Pleistocene watervoerende pakket (P_S1_PL);
* scenario met een gefundeerde Holocene zandlaag (P_S2_HL_F);
* scenario’s met een tussenzandlaag (P_S3_HL_TZ). Opbarsten vanuit het diepe pakket onder de scheidende laag vindt niet plaats.

Hiernaast zijn nog drie scenario’s aangemaakt om overige grondopbouwen in te kunnen schematiseren. Deze zijn opeenvolgend P_S4, P_S5 en P_S6 en naar eigen keuze in te delen.

De veranderlijke opeenvolging van laagscheidingen in de Holocene ondoorlatende deklaag is niet als scenario meegenomen. Deze variaties zijn opgenomen in de keuze van het gemiddeld volumegewicht van de deklaag per vak, dat per scenario en per vak bepaald kan worden. De opbouw van de deklaag (met name veel of weinig veen) is een criterium voor de geotechnische vakindeling.
