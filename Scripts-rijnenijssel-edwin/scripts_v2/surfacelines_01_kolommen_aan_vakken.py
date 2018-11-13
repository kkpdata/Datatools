# --------------------------------------------------------------------------
# Vakken FC aanmaken obv een kopie van het normtraject
# Kolommen aanmaken tbv Ringtoets 
# Maakt een kopie van de normtrajectlijn en voegt de kolommen toe.
# Witteveen+Bos
# ing. H.E.J. Nieuwland - augustus/november 2017
# update jan 2018 tbv Piping en Macro
# update mei 2018 XML kolommen toegevoegd
# --------------------------------------------------------------------------
# versie 1.0.1
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
import string, os, sys, locale, arcpy
# INPUT
Norm     = sys.argv[1]    # In Normtraject FC PWK_GEO_NORMTRAJECT
Traject  = sys.argv[2]    # naam van het normtraject
VakFC    = sys.argv[3]    # Vakken FC
#---
Kols     = [["ID","TEXT","25"],["X0","DOUBLE",""],["Vaknaam","TEXT","25"], ["Aandachtspunten","TEXT","200"],["HRD_Name","TEXT","50"], ["UIT_CSV_Bestand","TEXT","250"],["REPROF_NAAM","TEXT","30"]]           # kolommenlijst
#---
arcpy.env.overwriteOutput = True
arcpy.AddMessage("  >>> ----------------------------------")
arcpy.AddMessage("  >>> Wegschrijven prfl ")
arcpy.AddMessage("  >>> ----------------------------------")
#---------------------------------------------------------
#---------------------------------------------------------
# --------  START ---------
#---------------------------------------------------------
# kopie maken van het Normtraject naar een prfl vakken FC
#---------------------------------------------------------
where_clause = '"TRAJECT_ID" = \''+Traject+'\''
arcpy.Select_analysis(Norm, VakFC, where_clause)
#---------------------------------------------------------
workspace = arcpy.Describe(VakFC).path
# Nu de kolommen toevoegen
for kol in Kols:
    if kol[2] == "":
        try:
            arcpy.AddMessage("Kolom ("+str(kol)+") toevoegen...")
            arcpy.AddField_management(VakFC, kol[0], kol[1])
            arcpy.AddMessage("toegevoegd...")
        except:
            arcpy.AddError("Kolom ("+str(kol)+") bestaat al! Controleer zelf of type en length juist zijn.")
    else:
        try:
            arcpy.AddMessage("Kolom ("+str(kol)+") toevoegen...")
            arcpy.AddField_management(VakFC, kol[0], kol[1], "", "", kol[2])
            arcpy.AddMessage("toegevoegd...")
        except:
            arcpy.AddError("Kolom ("+str(kol)+") bestaat al! Controleer zelf of type en length juist zijn.")
#---------------------------------------------------------
arcpy.AddMessage("  >>> ----------------------------------")
arcpy.AddMessage("  >>> Aanmaken XML_* kolommen ")
arcpy.AddMessage("  >>> ----------------------------------")
#---------------------------------------------------------
#---------------------------------------------------------
# ----  START
#---------------------------------------------------------
#---------------------------------------------------------
# Domein aanmaken
domDicts =      {'Piping_JN' : ['true','false']}
# loopen om domein aan te maken en waarden toe te voegen
try:
    for domDict in domDicts:
        arcpy.AddMessage("Domein aanmaken: " + domDict)
        arcpy.CreateDomain_management(workspace, domDict, domDict, "TEXT", "CODED")
        for code in domDicts[domDict]:
            arcpy.AddMessage(" "+code)
            arcpy.AddCodedValueToDomain_management(workspace, domDict, code, code)
except:
    arcpy.AddMessage("Geen domeinen toegevoegd. Zijn al aanwezig!")
            
# Kolommen toevoegen incl. domein
try:
    arcpy.AddField_management(VakFC, "XML_Mapnaam", "TEXT", "", "", 50)
except:
    arcpy.AddError("Kolom XML_Mapnaam bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddField_management(VakFC, "XML_intredepunt", "DOUBLE")
except:
    arcpy.AddError("Kolom XML_intredepunt bestaat al! Controleer zelf of type en length juist zijn.")    
try:
    arcpy.AddField_management(VakFC, "XML_uittredepunt", "DOUBLE")
except:
    arcpy.AddError("Kolom XML_uittredepunt bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddField_management(VakFC, "XML_VerwachtingswaardePolderpeil", "DOUBLE")
except:
    arcpy.AddError("Kolom XML_VerwachtingswaardePolderpeil bestaat al! Controleer zelf of type en length juist zijn.")    
try:
    arcpy.AddField_management(VakFC, "XML_StandaardafwijkingPolderpeil", "DOUBLE")
except:
    arcpy.AddError("Kolom XML_StandaardafwijkingPolderpeil bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddField_management(VakFC, "XML_VerwachtingswaardeDempingsfactor", "DOUBLE")
except:
    arcpy.AddError("Kolom XML_VerwachtingswaardeDempingsfactor bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddField_management(VakFC, "XML_StandaardafwijkingDempingsfactor", "DOUBLE")
except:
    arcpy.AddError("Kolom XML_StandaardafwijkingDempingsfactor bestaat al! Controleer zelf of type en length juist zijn.")
# Deze info wordt uit het Soil bestand uitgelezen en kan hier niet worden ingevoerd 
##try:
##    arcpy.AddField_management(VakFC, "XML_ScenarioGebruiken", "TEXT", "", "", 5, "", "NULLABLE", "NON_REQUIRED", "Piping_JN")
##except:
##    arcpy.AddError("Kolom XML_ScenarioGebruiken bestaat al! Controleer zelf of type en length juist zijn.")  
##try:
##    arcpy.AddField_management(VakFC, "XML_ScenarioBijdrage", "DOUBLE")
##except:
##    arcpy.AddError("Kolom XML_ScenarioBijdrage bestaat al! Controleer zelf of type en length juist zijn.")
#---------------------------------------------------------
# enkele kolommen krijgen default waarde.
arcpy.CalculateField_management(in_table=VakFC, field="XML_StandaardafwijkingPolderpeil", expression='0.1', expression_type="PYTHON_9.3")
arcpy.CalculateField_management(in_table=VakFC, field="XML_VerwachtingswaardeDempingsfactor", expression='0.7', expression_type="PYTHON_9.3")
arcpy.CalculateField_management(in_table=VakFC, field="XML_StandaardafwijkingDempingsfactor", expression='0.1', expression_type="PYTHON_9.3")

#---------------------------------------------------------    
arcpy.AddMessage("\n  >>>  KLAAR!  <<<")
arcpy.AddMessage("\n  >>>  Kolommen toegevoegd aan:  \n\n  >>>  " + VakFC + "\n")
