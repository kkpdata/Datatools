# --------------------------------------------------------------------------
# Witteveen+Bos
# ing. H.E.J. Nieuwland - juli 2018
# --------------------------------------------------------------------------
# versie 1.0.1
# --------------------------------------------------------------------------
# Bepaal van gekozen representatief profiel het snijpunt met de piping in en uit trede lijnen.
# Update 5juni2018 Vaklijst None verwijderen.
# --------------------------------------------------------------------------
import string, os, sys, locale, arcpy
# INPUT
VakFC       = sys.argv[1]                 # Vakken FC
pipIN       = sys.argv[2]                 # FC met 1 piping intrede lijn. 
pipUIT      = sys.argv[3]                 # FC met 1 piping uittrede lijn. 
lnFC        = sys.argv[4]                 # PWK_GEO_PROFIELLIJNEN
kol         = "PIP_afstand"               # Nieuw aan te maken kolom aan het profiellijnen bestand
LnmKol      = "PROFIELNAAM"               # kolom met profielnaam
MedKol      = "MEDIAAN"                   # kolom met mediaan
ReprProfkol = "RepresentatiefProfiel"     # kolom waar de gebruiker in kan aangeven of het profiel representatief is.
Ofc         = "PROFIELLIJN_MEDIAAN"       # de uitvoer FC met de profiellijnen + mediaan en PIP afstand
lay         = os.path.dirname(__file__)+"/PROFIELLIJN_MEDIAAN.lyr"
#---
arcpy.env.overwriteOutput = True
arcpy.AddMessage("  >>> -------------------------------------")
arcpy.AddMessage("  >>> Snijpunt met profiel bepalen... ")
arcpy.AddMessage("  >>> -------------------------------------")
#---------------------------------------------------------
#---------------------------------------------------------
# ----  START  ----
#---------------------------------------------------------
workspace = arcpy.Describe(VakFC).path
arcpy.env.workspace = workspace
domein = "JA_NEE"
try:
  arcpy.CreateDomain_management(workspace, domein, domein, "TEXT", "CODED", "DEFAULT", "DEFAULT")
  for val in ["Ja","Nee"]:
    arcpy.AddCodedValueToDomain_management(in_workspace=workspace, domain_name=domein, code=val, code_description=val)
except:
  arcpy.AddMessage("Domein bestaat al.")
#----
# databasedir bepalen
workspace = arcpy.Describe(lnFC).path
arcpy.env.workspace = workspace
sr = arcpy.SpatialReference(28992)
# de 2 stukken profiellijn samenvoegen - De richting van de lijn is hierdoor niet altijd juist!!
arcpy.Dissolve_management(lnFC, "in_memory/xxProfLNdis", LnmKol)
# Piping niet altijd 1 lijn dus alles samenvoegen tot 1 multipart
#n = len(list(i for i in arcpy.da.SearchCursor(pipIN,"OID@")))
#arcpy.AddMessage("Er is/zijn: "+str(n)+" pipIN!")
arcpy.Dissolve_management(pipIN, "in_memory/xxpipIN")
n = len(list(i for i in arcpy.da.SearchCursor("in_memory/xxpipIN","OID@")))
arcpy.AddMessage("Er is/zijn: "+str(n)+" xxpipIN!")
# uittredelijn
#n = len(list(i for i in arcpy.da.SearchCursor(pipUIT,"OID@")))
#arcpy.AddMessage("Er is/zijn: "+str(n)+" pipUIT!")
arcpy.Dissolve_management(pipUIT, "in_memory/xxpipUIT")
n = len(list(i for i in arcpy.da.SearchCursor("in_memory/xxpipUIT","OID@")))
arcpy.AddMessage("Er is/zijn: "+str(n)+" xxpipUIT!")
#---------------------------------------------------------
# 1 vaknaam koppelen aan dwarsprofielen.
# Create a new fieldmappings and add the two input feature classes.
fieldmap = arcpy.FieldMappings()
fieldmap.addTable(lnFC)
fieldmap.addTable(VakFC)
arcpy.SpatialJoin_analysis(target_features="in_memory/xxProfLNdis", join_features=VakFC, out_feature_class=Ofc, join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_ALL", field_mapping=fieldmap, match_option="CLOSEST", search_radius="5 Meters")
fieldmap.removeAll()
arcpy.AddField_management(Ofc, kol, "DOUBLE")
arcpy.AddField_management(Ofc, MedKol, "TEXT", "", "", 8)
arcpy.AddField_management(Ofc, ReprProfkol, "TEXT", "", "", 25, "", "", "", domein)
#---------------------------------------------------------
# Representatief kolom op Nee zetten.
arcpy.CalculateField_management(in_table=Ofc, field=ReprProfkol, expression='"Nee"', expression_type="PYTHON_9.3")
#---------------------------------------------------------
# 1 Nu door de dwarsprofiellijnen loopen obv PROFIELNAAM
VAKkols = "SHAPE@","Vaknaam","ID",kol,LnmKol,MedKol
n = len(list(i for i in arcpy.da.SearchCursor(Ofc, VAKkols)))
arcpy.AddMessage("Er is/zijn: "+str(n)+" dwarsprofielen!")
r = 0
vaklijst = []
# PIPin geometry uitlezen
with arcpy.da.SearchCursor("in_memory/xxpipIN", ["SHAPE@"]) as Pcursor:
  for pip in Pcursor:
    PIPin = pip[0]
# PIPuit geometry uitlezen
with arcpy.da.SearchCursor("in_memory/xxpipUIT", ["SHAPE@"]) as Pcursor:
  for pip in Pcursor:
    PIPuit = pip[0]
with arcpy.da.UpdateCursor(Ofc, VAKkols) as cursor:
    for row in cursor:
        arcpy.AddMessage("  -------------------------------------")
        r = r +1
        SnijPunt = arcpy.Point(0,0)
        SnijPunt2 = arcpy.Point(0,0)
        arcpy.AddMessage(str(r)+" van "+str(n))
        vaklijst.append(row[1])
        #arcpy.AddMessage("  Vaknaam: "+str(row[1]))
        #arcpy.AddMessage("  ID: "+str(row[2]))
        #arcpy.AddMessage("  PIP afst: "+str(row[3]))
        #arcpy.AddMessage("  Profielnaam: "+str(row[4]))
        DeLijn = row[0]
        #arcpy.AddMessage("DeLijn = "+str(DeLijn.type))
        # Nu snijpunt van de piping lijnen vinden
        # snijpunt bepalen en wegschrijven
        PP = PIPin.intersect(DeLijn, 1)
        if PP.type != 'polyline':
            for p in PP:
                SnijPunt = p
        afstand = DeLijn.measureOnLine(SnijPunt)
        #arcpy.AddMessage("  Snijpunt in = "+str(round(afstand,2))+"m")
        pIN = round(afstand,2)
        # snijpunt bepalen en wegschrijven
        PP2 = PIPuit.intersect(DeLijn, 1)        
        if PP2.type != 'polyline':
            for p in PP2:
                SnijPunt2 = p
        afstand = DeLijn.measureOnLine(SnijPunt2)
        #arcpy.AddMessage("  Snijpunt uit = "+str(round(afstand,2))+"m")
        pUIT = round(afstand,2)          
        pDT = abs(pUIT - pIN) # afstand tussen de piping lijnen. Ook bij geflipte lijn 
        #arcpy.AddMessage("  Afstand tussen de piping lijnen = "+str(round(pDT,2))+"m")
        row[3] = round(pDT,2)
        # het vak updaten.
        cursor.updateRow(row)
    arcpy.AddMessage("-------------------------------------")
#-----------------
vaklijst = list(set(vaklijst))
vaklijst = list(filter(lambda x: x!= None, vaklijst))       # None uit de lijst halen anders loopt de routine vast
arcpy.AddMessage("Er is/zijn: "+str(len(vaklijst))+" vakken!")
if len(vaklijst) > 0:
  for vak in vaklijst:
    arcpy.AddMessage("  Vaknaam: "+str(vak))
    # nu alle dwarsprfiellijnen per vak selecteren en PIP_afstand uitlezen
    PIPlijst = []
    were = "Vaknaam = '"+str(vak)+"'"
    # alle PIP afstanden uitlezen in een array
    with arcpy.da.SearchCursor(Ofc, ["Vaknaam",kol], where_clause=were) as cursor:
        for row in cursor:
            PIPlijst.append(row[1])
    # mediaan bepalen.
    PIPlijst.sort()
    nPIP = len(PIPlijst)
    # Als er 2x dezelfde lijn is geselecteerd. dan zijn alle afstanden 0 en de som ook 0 dus dan niet verder gaan.
    if sum(PIPlijst) > 0 :
      # pip sorteren en middelste selecteren
      mid = int(round((nPIP / 2),0)) - 1
      dePIP = PIPlijst[mid]
      arcpy.AddMessage("  mediaan: "+str(dePIP))
      # het profiel van de mediaan selecteren en mediaan in de kolom MedKol zetten.
      were2 = "Vaknaam = '"+str(vak)+"' AND "+kol+" = "+str(dePIP)
      with arcpy.da.UpdateCursor(Ofc, ["Vaknaam",kol,MedKol,ReprProfkol], where_clause=were2) as cursor:
          for row in cursor:
              row[2] = 'Mediaan'
              row[3] = 'Ja'
              arcpy.AddMessage("  Mediaan bepaald!")
              # het profiel updaten.
              cursor.updateRow(row)
    else:
      arcpy.AddWarning("  Mediaan NIET bepaald!\n  Alle afstanden zijn 0. Lijkt er op dat dezelfde lijn 2x is gebruikt!")
else:
  arcpy.AddWarning("  Mediaan NIET bepaald!\n  er zijn geen profielen die op een vak liggen.")
#------------------------------------
# toevoegen aan TOC
MXD = arcpy.mapping.MapDocument("CURRENT")
DF = arcpy.mapping.ListDataFrames(MXD)[0]            
lyr2 = arcpy.mapping.Layer(lay)
lyr2.replaceDataSource(workspace,"FILEGDB_WORKSPACE",Ofc)
for lyr in arcpy.mapping.ListLayers(MXD, "", DF):
    if lyr.name == lyr2.name:
        arcpy.mapping.RemoveLayer(DF, lyr)
        arcpy.AddMessage("bestaande layer verwijderen!")
arcpy.mapping.AddLayer(DF, lyr2, "TOP")
#------------------------------------
arcpy.AddMessage("\n  >>>  KLAAR!  <<<")
