# Datatool voor kunstwerkparameters

Ontwikkeld door: 
* Alfred M. Drenth
* Waterschap Noorderzijlvest
* 31/jan/2018


# Beschrijving tool

Excelfile om op gestructureerde wijze parameterwaarden te verzamelen. Hiervan wordt vervolgens een kolom gevuld met de waarden voor een CSV-file. Deze CSV-file kan als importfile gebruikt worden in Ringtoets. De parameters zijn noodzakelijk voor de berekeningen bij

* Hoogte Kunstwerk (HTKW)
* Betrouwbaarheid Sluiting Kunstwerk (BSKW)
* Sterkte en Stabiliteit Puntconstructies (STKWp)

Werkblad '1e' bevat de in  te vullen velden.
Werkblad 'Default waarden' bevat gegevens die door '1e' wordt aangeroepen. Als werkblad '1e' wordt vermeerderd, vanwege meerdere kunstwerken, dan geldt 'Default waarde' ook voor deze vervolgwerkbladen.


# Werkwijze

Alleen de velden in kolom F of G hoeven ingevuld te worden. De grijze worden dan automatisch gevuld. Toets F9 als dit niet automatisch gaat.

In kolom O verschijnt de waarde voor de CSV-file. Deze kolom wordt opgebouwd adhv de (verborgen) kolommen M en N waarmee bepaald wordt welke waarde getoond worden en in welke volgorde. Lege regels worden genegeerd. 

Kopieer de gevulde velden O7 - O56 naar een vrije kolom (plakken/waarden)
Kopieer vervolgens die waarden naar een textbestand en sla dat op met de extensie <.csv>.


Meerdere kunstwerken? Kopieer het gehele werblad '1e' naar een volgend werkblad.


# Uit de handleiding RINGTOETS

Bij het importeren van de gegevens met betrekking tot kunstwerken vraagt RINGTOETS om een locatiebestand (Extensie <.shp>) [Ringtoets handleiding paragraaf 3.5.3.2] met daarin de kunstwerklocaties. Vervolgens koppelt RINGTOETS dit locatiebestand met de naam <Bestandsnaam.shp> aan een bijbehorend CSV-bestand met de naam <Bestandsnaam.csv> waarin de eigenschappen van de kunstwerken zijn opgenomen.

De eigenschappen van kunstwerken worden geschematiseerd in een CSV-bestand [Ringtoets handleiding paragraaf 3.5.3.1] waarvan de bestandsnaam correspondeert met de bestandsnaam van de locaties van het kunstwerk [Ringtoets handleiding paragraaf 12.2.1]. 

Voor het CSV-bestand gelden de volgende regels:
* Alle velden in elke regel moeten gescheiden worden door middel van een puntkomma (;).
* De decimalen moeten achter een punt (.) geschreven worden.
* De eerste regel bevat de veldnamen waarmee de kunstwerken worden beschreven:  Identificatie;Kunstwerken.identificatie;AlfaNumeriekeWaarde;NumeriekeWaarde;Standaardafwijking.variatie;Boolean.

De volgende regels beschrijven de fysieke eigenschappen van de kunstwerken, in de volgorde van de velden zoals weergegeven in de kopregel. Van elk te beoordelen kunstwerk dient minimaal één eigenschap te worden ingevoerd. De gebruiker heeft de mogelijkheid om deze fysieke eigenschappen in de berekeningen aan te passen of aan te vullen [Ringtoets handleiding paragraaf 12.3.1].