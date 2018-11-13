# --------------------------------------------------------------------------
# Vakken FC aanmaken obv een kopie van het normtraject
# Kolommen aanmaken tbv Ringtoets
# Maakt een kopie van de normtrajectlijn en voegt de kolommen toe.
# Witteveen+Bos
# ing. H.E.J. Nieuwland - augustus/november 2017
# --------------------------------------------------------------------------
# versie 1.0.2
# --------------------------------------------------------------------------
# 20180501 - update XML kolommen toegevoegd
# 20180711 - nu toevoegen van alle kolommen in deze stap.
# --------------------------------------------------------------------------
import string, os, sys, locale, arcpy
from time import strftime  
tijd = strftime("%m-%d-%Y %H:%M:%S")
# INPUT
Norm     = sys.argv[1]    # In Normtraject FC PWK_GEO_NORMTRAJECT
Traject  = sys.argv[2]    # naam van het normtraject
VakFC    = sys.argv[3]    # Vakken FC
Kols     = [["ID","TEXT","25"],["X0","DOUBLE",""],["Vaknaam","TEXT","25"],["Aandachtspunten","TEXT","200"],["TALUDID","TEXT","25"],["CONTROLE_Buitentalud","FLOAT",""],["CONTROLE_Binnentalud","FLOAT",""], ["HRD_Name","TEXT","50"], ["UIT_PRFL_Bestand","TEXT","250"], ["CONTROLE_Buitentalud","FLOAT","5","1"], ["CONTROLE_Binnentalud","FLOAT","5","1"] ]           # kolommenlijst
#---
arcpy.env.overwriteOutput = True
arcpy.AddMessage(">>> ----------------------------------")
arcpy.AddMessage(">>> Wegschrijven prfl vakken")
arcpy.AddMessage(">>> ----------------------------------")
#---------------------------------------------------------
#---------------------------------------------------------
# ------  START ------
#---------------------------------------------------------
# kopie maken van het Normtraject naar een prfl vakken FC
#---------------------------------------------------------
where_clause = '"TRAJECT_ID" = \''+Traject+'\''
arcpy.Select_analysis(Norm, VakFC, where_clause)
#---------------------------------------------------------
workspace = arcpy.Describe(VakFC).path
#---------------------------------------------------------
# Domeinen aanmaken
# Kolommen aan Toetsvakken toevoegen incl. domeinen voor invullen keuzes tbv prfl.
# Grasmat kwaliteit, Kleilaagdikte, Golfhoogteklasse en check Toepassingsvoorwaarde
domDicts =      {'GrasmatKwaliteit' : ['open', 'fragmentarisch', 'gesloten']}
domDicts.update ({'Kleilaagdikte' : ['groter dan 0.4m','kleiner dan 0.4m']})
domDicts.update ({'Golfhoogteklasse' : ['0-1m','1-2m','2-3m','< 3m']})
domDicts.update ({'Type dijk' : ['groene dijk','damwand']})
domDicts.update ({'Toepassingsvoorwaarde' : ['ja','nee']})
domDicts.update ({'HBNberekenen' : ['niet', 'norm', 'doorsnede']})
domDicts.update ({'GEKB_JN' : ['true','false']})
domDicts.update ({'DamType' : ['verticalewand','caisson','havendam']})
# loopen om domein aan te maken en waarden toe te voegen
for domDict in domDicts:
    try:
        arcpy.AddMessage("Domein aanmaken: " + domDict)
        arcpy.CreateDomain_management(workspace, domDict, domDict, "TEXT", "CODED")
        for code in domDicts[domDict]:
            arcpy.AddMessage(" "+code)
            arcpy.AddCodedValueToDomain_management(workspace, domDict, code, code)
    except:
        arcpy.AddWarning("Geen domein toegevoegd! Is al aanwezig.")
# Range Domein voor de ruwheden aanmaken 0.5-1.0
arcpy.AddMessage("Domein Ruwheid aanmaken...")
try:
    arcpy.CreateDomain_management(in_workspace=workspace, domain_name="Ruwheid", domain_description="Ruwheid", field_type="FLOAT", domain_type="RANGE", split_policy="DEFAULT", merge_policy="DEFAULT")
    arcpy.SetValueForRangeDomain_management(in_workspace=workspace, domain_name="Ruwheid", min_value="0.5", max_value="1.0")
except:
    arcpy.AddWarning("Geen domein toegevoegd. Is al aanwezig!")
arcpy.AddWarning("\n")
#---------------------------------------------------------
#---------------------------------------------------------
# Nu de kolommen toevoegen incl. domein
#---------------------------------------------------------
for kol in Kols:
    if kol[2] == "":
        try:
            arcpy.AddMessage("Kolom "+str(kol[0])+" toevoegen...")
            arcpy.AddField_management(VakFC, kol[0], kol[1])
        except:
            arcpy.AddError("Kolom "+str(kol[0])+" bestaat al! Controleer zelf of type en length juist zijn.")
    else:
        try:
            arcpy.AddMessage("Kolom "+str(kol[0])+" toevoegen...")
            arcpy.AddField_management(VakFC, kol[0], kol[1], "", "", kol[2])
        except:
            arcpy.AddError("Kolom "+str(kol[0])+" bestaat al! Controleer zelf of type en length juist zijn.")
# Kolommen toevoegen incl. domein
try:
    arcpy.AddMessage("Kolom GrasmatKwaliteit_binnen toevoegen...")
    arcpy.AddField_management(VakFC, "GrasmatKwaliteit_binnen", "TEXT", "", "", 15, "", "NULLABLE", "NON_REQUIRED", "GrasmatKwaliteit")
except:
    arcpy.AddError("Kolom GrasmatKwaliteit_binnen bestaat al! Controleer zelf of type en length juist zijn.")  
try:
    arcpy.AddMessage("Kolom KleilaagDikte_binnen toevoegen...")
    arcpy.AddField_management(VakFC, "KleilaagDikte_binnen", "TEXT", "", "", 18, "", "NULLABLE", "NON_REQUIRED", "Kleilaagdikte")
except:
    arcpy.AddError("Kolom KleilaagDikte_binnen bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom GolfHoogteKlasse toevoegen...")
    arcpy.AddField_management(VakFC, "GolfHoogteKlasse", "TEXT", "", "", 5, "", "NULLABLE", "NON_REQUIRED", "Golfhoogteklasse")
except:
    arcpy.AddError("Kolom GolfHoogteKlasse bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom Toepassingsvoorwaarde toevoegen...")
    arcpy.AddField_management(VakFC, "Toepassingsvoorwaarde", "TEXT", "", "", 3, "", "NULLABLE", "NON_REQUIRED", "Toepassingsvoorwaarde")
except:
    arcpy.AddError("Kolom Toepassingsvoorwaarde bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom TypeDijk toevoegen...")
    arcpy.AddField_management(VakFC, "TypeDijk", "TEXT", "", "", 15, "", "NULLABLE", "NON_REQUIRED", "Type dijk")
except:
    arcpy.AddError("Kolom TypeDijk bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom Ruw_BuiTal_1 toevoegen...")
    arcpy.AddField_management(VakFC, "Ruw_BuiTal_1", "FLOAT", 3, 1, "", "", "NULLABLE", "NON_REQUIRED", "Ruwheid")
except:
    arcpy.AddError("Kolom Ruw_BuiTal_1 bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom Ruw_BuiTal_2 toevoegen...")
    arcpy.AddField_management(VakFC, "Ruw_BuiTal_2", "FLOAT", 3, 1, "", "", "NULLABLE", "NON_REQUIRED", "Ruwheid")
except:
    arcpy.AddError("Kolom Ruw_BuiTal_2 bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom Ruw_BuiTal_3 toevoegen...")
    arcpy.AddField_management(VakFC, "Ruw_BuiTal_3", "FLOAT", 3, 1, "", "", "NULLABLE", "NON_REQUIRED", "Ruwheid")
except:
    arcpy.AddError("Kolom Ruw_BuiTal_3 bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom Ruw_BuiTal_4 toevoegen...")
    arcpy.AddField_management(VakFC, "Ruw_BuiTal_4", "FLOAT", 3, 1, "", "", "NULLABLE", "NON_REQUIRED", "Ruwheid")
except:
    arcpy.AddError("Kolom Ruw_BuiTal_4 bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom Ruw_BuiTal_5 toevoegen...")
    arcpy.AddField_management(VakFC, "Ruw_BuiTal_5", "FLOAT", 3, 1, "", "", "NULLABLE", "NON_REQUIRED", "Ruwheid")
except:
    arcpy.AddError("Kolom Ruw_BuiTal_5 bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom PRFL_Helling_1 toevoegen...")
    arcpy.AddField_management(VakFC, "PRFL_Helling_1", "FLOAT", 6, 2)
except:
    arcpy.AddError("Kolom PRFL_Helling_1 bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom PRFL_Helling_2 toevoegen...")
    arcpy.AddField_management(VakFC, "PRFL_Helling_2", "FLOAT", 6, 2)
except:
    arcpy.AddError("Kolom PRFL_Helling_2 bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom PRFL_Helling_3 toevoegen...")
    arcpy.AddField_management(VakFC, "PRFL_Helling_3", "FLOAT", 6, 2)
except:
    arcpy.AddError("Kolom PRFL_Helling_3 bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom PRFL_Helling_4 toevoegen...")
    arcpy.AddField_management(VakFC, "PRFL_Helling_4", "FLOAT", 6, 2)
except:
    arcpy.AddError("Kolom PRFL_Helling_4 bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom PRFL_Helling_5 toevoegen...")
    arcpy.AddField_management(VakFC, "PRFL_Helling_5", "FLOAT", 6, 2)
except:
    arcpy.AddError("Kolom PRFL_Helling_5 bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom PRFL_DijkNormaal toevoegen...")
    arcpy.AddField_management(VakFC, "PRFL_DijkNormaal", "FLOAT", 5, 2)
except:
    arcpy.AddError("Kolom PRFL_DijkNormaal bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom PRFL_Zetting toevoegen...")
    arcpy.AddField_management(VakFC, "PRFL_Zetting", "FLOAT", 4, 2)
except:
    arcpy.AddError("Kolom PRFL_Zetting bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom PRFL_KruinHgt toevoegen...")
    arcpy.AddField_management(VakFC, "PRFL_KruinHgt", "FLOAT", 4, 2)
except:
    arcpy.AddError("Kolom PRFL_KruinHgt bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom PRFL_Opmerkingen toevoegen...")
    arcpy.AddField_management(VakFC, "PRFL_Opmerkingen", "TEXT", "", "", 200)
except:
    arcpy.AddError("Kolom PRFL_Opmerkingen bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom Opmerkingen_ProfielMaken toevoegen...")
    arcpy.AddField_management(VakFC, "Opmerkingen_ProfielMaken", "TEXT", "", "", 250)
except:
    arcpy.AddError("Kolom Opmerkingen_ProfielMaken bestaat al! Controleer zelf of type en length juist zijn.")
#------------
# default value aan de ruwheids kolommen zetten. Alles op 1
arcpy.AssignDefaultToField_management(in_table=VakFC, field_name="Ruw_BuiTal_1", default_value="1", subtype_code="", clear_value="false")
arcpy.AssignDefaultToField_management(in_table=VakFC, field_name="Ruw_BuiTal_2", default_value="1", subtype_code="", clear_value="false")
arcpy.AssignDefaultToField_management(in_table=VakFC, field_name="Ruw_BuiTal_3", default_value="1", subtype_code="", clear_value="false")
arcpy.AssignDefaultToField_management(in_table=VakFC, field_name="Ruw_BuiTal_4", default_value="1", subtype_code="", clear_value="false")
arcpy.AssignDefaultToField_management(in_table=VakFC, field_name="Ruw_BuiTal_5", default_value="1", subtype_code="", clear_value="false")
#---------------------------------------------------------
#---------------------------------------------------------
# Nu de XML kolommen en domeinen toevoegen.
#---------------------------------------------------------
# Kolommen toevoegen incl. domein
try:
    arcpy.AddMessage("Kolom XML_Mapnaam toevoegen...")
    arcpy.AddField_management(VakFC, "XML_Mapnaam", "TEXT", "", "", 50)
except:
    arcpy.AddError("Kolom XML_Mapnaam bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom XML_HBNberekenen toevoegen...")
    arcpy.AddField_management(VakFC, "XML_HBNberekenen", "TEXT", "", "", 15, "", "NULLABLE", "NON_REQUIRED", "HBNberekenen")
except:
    arcpy.AddError("Kolom XML_HBNberekenen bestaat al! Controleer zelf of type en length juist zijn.")    
try:
    arcpy.AddMessage("Kolom XML_OverslagdebietBerekenen toevoegen...")
    arcpy.AddField_management(VakFC, "XML_OverslagdebietBerekenen", "TEXT", "", "", 15, "", "NULLABLE", "NON_REQUIRED", "HBNberekenen")
except:
    arcpy.AddError("Kolom XML_OverslagdebietBerekenen bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom XML_IllustratiePntInlezen toevoegen...")
    arcpy.AddField_management(VakFC, "XML_IllustratiePntInlezen", "TEXT", "", "", 5, "", "NULLABLE", "NON_REQUIRED", "GEKB_JN")
except:
    arcpy.AddError("Kolom XML_IllustratiePntInlezen bestaat al! Controleer zelf of type en length juist zijn.")    
try:
    arcpy.AddMessage("Kolom XML_HBNillustratiePntInlezen toevoegen...")
    arcpy.AddField_management(VakFC, "XML_HBNillustratiePntInlezen", "TEXT", "", "", 5, "", "NULLABLE", "NON_REQUIRED", "GEKB_JN")
except:
    arcpy.AddError("Kolom XML_HBNillustratiePntInlezen bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom XML_OverslagDebietIllustratiePntInlezen toevoegen...")
    arcpy.AddField_management(VakFC, "XML_OverslagDebietIllustratiePntInlezen", "TEXT", "", "", 5, "", "NULLABLE", "NON_REQUIRED", "GEKB_JN")
except:
    arcpy.AddError("Kolom XML_OverslagDebietIllustratiePntInlezen bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom XML_DamGebruiken toevoegen...")
    arcpy.AddField_management(VakFC, "XML_DamGebruiken", "TEXT", "", "", 5, "", "NULLABLE", "NON_REQUIRED", "GEKB_JN")
except:
    arcpy.AddError("Kolom XML_DamGebruiken bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom XML_DamType toevoegen...")
    arcpy.AddField_management(VakFC, "XML_DamType", "TEXT", "", "", 15, "", "NULLABLE", "NON_REQUIRED", "DamType")
except:
    arcpy.AddError("Kolom XML_DamType bestaat al! Controleer zelf of type en length juist zijn.")  
try:
    arcpy.AddMessage("Kolom XML_DamHoogte toevoegen...")
    arcpy.AddField_management(VakFC, "XML_DamHoogte", "DOUBLE")
except:
    arcpy.AddError("Kolom XML_DamHoogte bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom XML_VoorlandGebruiken toevoegen...")
    arcpy.AddField_management(VakFC, "XML_VoorlandGebruiken", "TEXT", "", "", 5, "", "NULLABLE", "NON_REQUIRED", "GEKB_JN")
except:
    arcpy.AddError("Kolom XML_VoorlandGebruiken bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom XML_VerwachtingsWaarde toevoegen...")
    arcpy.AddField_management(VakFC, "XML_VerwachtingsWaarde", "DOUBLE")
except:
    arcpy.AddError("Kolom XML_VerwachtingsWaarde bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom XML_StandaardAfwijking toevoegen...")
    arcpy.AddField_management(VakFC, "XML_StandaardAfwijking", "DOUBLE")
except:
    arcpy.AddError("Kolom XML_StandaardAfwijking bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddMessage("Kolom UIT_XML_Bestand toevoegen...")
    arcpy.AddField_management(VakFC, "UIT_XML_Bestand", "TEXT", "", "", 250)
except:
    arcpy.AddError("Kolom UIT_XML_Bestand bestaat al! Controleer zelf of type en length juist zijn.")
#---------------------------------------------------------
arcpy.AddMessage("\n>>> ----------------------------------")
arcpy.AddMessage(">>> KLAAR! ")
arcpy.AddMessage(">>> Kolommen toegevoegd aan:  \n>>> " + VakFC)
arcpy.AddMessage(">>> ----------------------------------")
