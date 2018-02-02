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

Bij het importeren van de gegevens met betrekking tot kunstwerken vraagt RINGTOETS om een locatiebestand (Extensie <.shp>) [paragraaf 3.5.3.2] met daarin de kunstwerklocaties. Vervolgens koppelt RINGTOETS dit locatiebestand met de naam <Bestandsnaam.shp> aan een bijbehorend CSV-bestand met de naam <Bestandsnaam.csv> waarin de eigenschappen van de kunstwerken zijn opgenomen.
