# Inleiding
`SOSscenarios_db_v3.py` is een Pythonscript om SOS-scenario's te visualiseren, ten behoeve van onder andere analyses en rapportages. Het script leest de gegevens automatisch uit uit de database en plot per segment alle scenario's, waarbij de kansen per scenario worden weergegeven.

*Auteur: M. Flierman, 2018*

## Vereisten
* Python 3.6
* D-SoilModel 17.1/17.2 (dit let niet bijster nauw, maar deze versies doen het sowieso)

# Randvoorwaarden  
Het script is op sommige plekken geënt op de precieze segmentnaamgeving zoals deze bij Aa en Maas wordt gehanteerd. Materialen worden bijvoorbeeld met `Segment_36013_P_Rg_zg` aangeduid. Op regel 69 wordt van deze naamgeving gebruik gemaakt door de materiaalnaam te extraheren met:

`summary['materiaal']= [seg.split('_',maxsplit=2)[2] for seg in summary.MA_Name]`

Het script is dus niet generiek opgezet maar kan met enkele kleine aanpassingen overgezet worden naar uw eigen systeem.

# Voorbeeld

![Voorbeeld SOS-plot](https://github.com/kkpdata/Datatools/raw/master/Scripts-aaenmaas-thijs/Plotten%20SOS-scenarios/voorbeeld_output.png "SOS-plot")
