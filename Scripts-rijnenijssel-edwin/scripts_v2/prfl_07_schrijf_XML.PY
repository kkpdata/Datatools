# --------------------------------------------------------------------------
# Wegschrijven naar *.XML tbv Ringtoets/Riskeer
# Witteveen+Bos
# ing. H.E.J. Nieuwland - juni 2018
# --------------------------------------------------------------------------
# versie 1.0.1
# --------------------------------------------------------------------------
# 18-06-2018 - kopie van 6(prfl en xml) nu alleen de losse xml wegschrijven.
# 08-08-2018 - v2 aanpassing script obv zelf ingevoerde teen en meerdere taludknikpunten.
# 22-08-2018 - aanpassing tbv de groene dijk/damwand export
# --------------------------------------------------------------------------
import string, os, sys, locale, arcpy
from xml.etree import ElementTree as ET
from time import strftime
tijd = strftime("%m-%d-%Y %H:%M:%S")

# INPUT
VakFC        = sys.argv[1]             # Lijnen FC met de vakken
IDkol        = "ID"                    # Kolom met id vak
Vkol         = "Vaknaam"               # Kolom met naam vak
odir         = sys.argv[2]             # uitvoer map
onaam        = sys.argv[3]             # naam van de uitvoer XML
normaal      = "PRFL_DijkNormaal"      # de normaal tov noorden van de profiellijn kolom Normaal
ruwheid      = 1.0                     # de standaard ruwheid
ruw_kol1     = "Ruw_BuiTal_1"          # ruwheid vanaf de kruin naar volgende punt
ruw_kol2     = "Ruw_BuiTal_2"          # ruwheid 2e segment
ruw_kol3     = "Ruw_BuiTal_3"          # ruwheid 3e segment
ruw_kol4     = "Ruw_BuiTal_4"          # ruwheid 4e segment
ruw_kol5     = "Ruw_BuiTal_5"          # ruwheid 5e segment
Typekol      = "TypeDijk"              # type moet groene dijk zijn damwand wordt in een andere routine speciaal voor Hydra-NL geexporteerd.
Uitkol       = "UIT_PRFL_Bestand"      # kolom waar het volledig path naar de prfl in kan worden weggeschreven. max. 250 anders alleen de naam

# domeinen voor controle XML invoer waarden
HBNberekenen = ['niet','norm','doorsnede']
GEKB_JN = ['true','false']
DamType = ['verticalewand','caisson','havendam']
# De benodigde kolommen voor het aanmaken van de XML.
kolommen = ["OID@","SHAPE@","ID","Vaknaam","PRFL_DijkNormaal", "PRFL_KruinHgt","XML_HBNberekenen","XML_OverslagdebietBerekenen","XML_IllustratiePntInlezen",
            "XML_HBNillustratiePntInlezen","XML_OverslagDebietIllustratiePntInlezen","XML_DamGebruiken","XML_DamType",
            "XML_DamHoogte","XML_VoorlandGebruiken","XML_VerwachtingsWaarde","XML_StandaardAfwijking", "XML_Mapnaam", "HRD_Name", "UIT_XML_Bestand"]

#--------------------------------------------------------------------------------------------------
# workspace databasedir bepalen
workspace = arcpy.Describe(VakFC).path
arcpy.env.workspace = workspace
#--------------------------------------------------------------------------------------------------
# volgende 2 def's voor de XML
def indent(elem, level=0):
  i = "\n" + level*"  "
  if len(elem):
    if not elem.text or not elem.text.strip():
      elem.text = i + "  "
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
    for elem in elem:
      indent(elem, level+1)
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
  else:
    if level and (not elem.tail or not elem.tail.strip()):
      elem.tail = i

def controleerVak(rij):
  check = False
  Klijst = []
  CHKlijst = []
  # controleer of de waarden van het vak ingevoerd zijn en eventueel of ze logisch zijn.
  k = 2
  while k <= 17:
    #arcpy.AddMessage("K=  "+str(rij[k]))
    if str(rij[k]) == 'None':
      check = True
      Klijst.append(cursor.fields[k])
    else:
      # sommige kolommen controleren tov domein
      if k == 6:
        if str(rij[k]) not in HBNberekenen:
          check = True
          arcpy.AddError("Waarde in kolom: "+str(cursor.fields[k])+" niet juist!")
          Klijst.append(cursor.fields[k])
      elif k == 7:
        if str(rij[k]) not in HBNberekenen:
          check = True
          arcpy.AddError("Waarde in kolom: "+str(cursor.fields[k])+" niet juist!")
          Klijst.append(cursor.fields[k])
      elif k == 8:
        if str(rij[k]) not in GEKB_JN:
          check = True
          arcpy.AddError("Waarde in kolom: "+str(cursor.fields[k])+" niet juist!")
          Klijst.append(cursor.fields[k])
      elif k == 9:
        if str(rij[k]) not in GEKB_JN:
          check = True
          arcpy.AddError("Waarde in kolom: "+str(cursor.fields[k])+" niet juist!")
          Klijst.append(cursor.fields[k])
      elif k == 10:
        if str(rij[k]) not in GEKB_JN:
          check = True
          arcpy.AddError("Waarde in kolom: "+str(cursor.fields[k])+" niet juist!")
          Klijst.append(cursor.fields[k])
      elif k == 11:
        if str(rij[k]) not in GEKB_JN:
          check = True
          arcpy.AddError("Waarde in kolom: "+str(cursor.fields[k])+" niet juist!")
          Klijst.append(cursor.fields[k])
      elif k == 12:
        if str(rij[k]) not in DamType:
          check = True
          arcpy.AddError("Waarde in kolom: "+str(cursor.fields[k])+" niet juist!")
          Klijst.append(cursor.fields[k])
      elif k == 13:
        if rij[k] < 0 or rij[k] > 100:
          check = True
          arcpy.AddError("Waarde in kolom: "+str(cursor.fields[k])+" niet juist!")
          Klijst.append(cursor.fields[k])
      elif k == 14:
        if str(rij[k]) not in GEKB_JN:
          check = True
          arcpy.AddError("Waarde in kolom: "+str(cursor.fields[k])+" niet juist!")
          Klijst.append(cursor.fields[k])
      elif k == 15:
        if rij[k] < 0 or rij[k] > 100:
          check = True
          arcpy.AddError("Waarde in kolom: "+str(cursor.fields[k])+" niet juist!")
          Klijst.append(cursor.fields[k])
      elif k == 16:
        if rij[k] < 0 or rij[k] > 100:
          check = True
          arcpy.AddError("Waarde in kolom: "+str(cursor.fields[k])+" niet juist!")
          Klijst.append(cursor.fields[k])
    k = k+1
  CHKlijst.append(check)
  CHKlijst.append(Klijst)
  return CHKlijst
#---
arcpy.env.overwriteOutput = True
arcpy.AddMessage("\n  >>> ----------------------------------")
arcpy.AddMessage("  >>> Wegschrijven "+onaam+".XML ")
arcpy.AddMessage("  >>> ----------------------------------")
#---------------------------------------------------------------------------------------------------------------------------------------
#***************************************************************************************************************************************
# ----  START XML aanmaken ----
#***************************************************************************************************************************************
#---------------------------------------------------------------------------------------------------------------------------------------
# Voor het aanmaken van de XML
# per vak naam uitlezen, profielnamen selecteren en lijst van maken.
# Aantal vakken uitlezen.
waar = Typekol +" = 'groene dijk'"
countTOT = len(list(i for i in arcpy.da.SearchCursor(VakFC, kolommen)))
count = len(list(i for i in arcpy.da.SearchCursor(VakFC, kolommen, where_clause=waar)))
arcpy.AddMessage("\nAantal vakken: "+str(count)+" van "+str(countTOT)+" verwerken.")
#-------------------------
#-- De XML
uitXML = onaam+".xml"
arcpy.AddMessage("XML: "+uitXML+" aanmaken...")
#-------------------------
#1e deel XML aanmaken.
confEL = ET.Element("configuratie")
Mapnm = 'xxleeg'
##with arcpy.da.UpdateCursor(VakFC, kolommen, sql_clause=(None, 'ORDER BY XML_Mapnaam, ID')) as cursor:   # sorteren op Mapnaam en ID
with arcpy.da.UpdateCursor(VakFC, kolommen, where_clause=waar, sql_clause=(None, 'ORDER BY XML_Mapnaam,'+Vkol)) as cursor:   # sorteren op Mapnaam en ID
  for row in cursor:    
    FOUT = False   # als de benodigde variabelen niet juist zijn dan niet in de XML wegschrijven!
    arcpy.AddMessage("\n--------------------------------")
    arcpy.AddMessage("VakID: "+str(row[2]))
    arcpy.AddMessage("Naam: "+str(row[3]))
    #---------------------------------------------------------
    # kolomwaarden controleren.
    control = controleerVak(row)
    FOUT = control[0]
    Klijst = control[1]
    #---------------------------------------------------------
    # Ook even kijken of er wel een prfl van het vak bestaat! Zo niet dan alleen melden.
    Pfchk = False
    were = IDkol +" = '"+str(row[2])+"'"
    with arcpy.da.SearchCursor(VakFC, [IDkol,Uitkol], where_clause=were) as Pcursor:
        for prow in Pcursor:
            BestNaam = prow[1]
    try:
        Pfchk = arcpy.Exists(BestNaam)
    except:
        Pfchk = False
    if not Pfchk:
        arcpy.AddWarning("> Let op!: Dit vak heeft geen prfl file!\n> Berekening wordt niet aangemaakt!")
    #---------------------------------------------------------
    #-- De XML aanmaken
    if FOUT == False and Pfchk:
      if Mapnm != row[17]:
        mapEL  = ET.SubElement(confEL,"map")
        mapEL.set("naam", str(row[17]))
        Mapnm = str(row[17])
      arcpy.AddMessage("berekening aanmaken...")
      # de berekening
      berekeningEL = ET.SubElement(mapEL,"berekening")
      berekeningEL.set("naam", str(row[3]))
      hrloc = ET.SubElement(berekeningEL, "hrlocatie")
      hrloc.text = str(row[18])
      hrd = ET.SubElement(berekeningEL, "dijkprofiel")
      hrd.text = str(row[2])
      # **** Kan worden uitgezet wordt gewoon van profiel overgenomen! ****
      profsch = ET.SubElement(berekeningEL, "orientatie")
      profsch.text = str(round(row[4],2))
      intr = ET.SubElement(berekeningEL, "dijkhoogte")
      intr.text = str(round(row[5],2))
      uittr = ET.SubElement(berekeningEL, "illustratiepunteninlezen")
      uittr.text = str(row[8])
      ond = ET.SubElement(berekeningEL, "hbnillustratiepunteninlezen")
      ond.text = str(row[9])
      onds = ET.SubElement(berekeningEL, "overslagdebietillustratiepunteninlezen")
      onds.text = str(row[10])
      onds = ET.SubElement(berekeningEL, "hbnberekenen")
      onds.text = str(row[6])
      onds = ET.SubElement(berekeningEL, "overslagdebietberekenen")
      onds.text = str(row[7])
      # **** Kan worden uitgezet wordt gewoon van profiel overgenomen! ****
      #-- Golfreductie --
      sto1 = ET.SubElement(berekeningEL, "golfreductie")
      dg = ET.SubElement(sto1, "damgebruiken")
      dg.text = str(row[11])
      verw = ET.SubElement(sto1, "damtype")
      verw.text = str(row[12])
      sd = ET.SubElement(sto1, "damhoogte")
      sd.text = str(round(row[13],2))
      vrl = ET.SubElement(sto1, "voorlandgebruiken")
      vrl.text = str(row[14])
      #-- Stochasten --
      sto = ET.SubElement(berekeningEL, "stochasten")
      sto1 = ET.SubElement(sto, "stochast")
      sto1.set("naam","overslagdebiet")                 # bij gekb altijd overslagdebiet.
      verw = ET.SubElement(sto1, "verwachtingswaarde")
      verw.text = str(row[15])
      sd = ET.SubElement(sto1, "standaardafwijking")
      sd.text = str(row[16])
      #--
      # Naam van de XML waarin het profiel is weggeschreven aan het vak koppelen. kolom=UIT_XML_Bestand
      row[19] = os.path.join(odir,uitXML)
      cursor.updateRow(row)
    else:
      if not Pfchk:
        arcpy.AddWarning("\nVak overgeslagen omdat er geen PRFL voor is aangemaakt!")
      else:
        arcpy.AddError("\nxx Vak overgeslagen te weinig informatie!")
        arcpy.AddError("xx De volgende kolommen zijn niet of niet juist ingevuld: \n"+str(Klijst))
del row, cursor
arcpy.AddMessage("\n--------------------------------")
# Nu de XML mooi opmaken
indent(confEL)
# wegschrijven naar XML file
tree = ET.ElementTree(confEL)
tree.write(odir+"/"+uitXML, xml_declaration=True, encoding='utf-8', method="xml")

arcpy.AddMessage("--  XML weggeschreven naar:  \n--  " + uitXML + "\n")
arcpy.AddMessage("--------------------------------")
arcpy.AddMessage("\n  >>>  KLAAR!  <<<\n")
