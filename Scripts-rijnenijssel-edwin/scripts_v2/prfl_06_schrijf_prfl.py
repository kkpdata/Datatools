# --------------------------------------------------------------------------
# Wegschrijven naar *.prfl tbv Ringtoets incl. punten shape
# we hebben alleen voorland, teen en kruin punten.
# Witteveen+Bos
# ing. H.E.J. Nieuwland - september 2017
# --------------------------------------------------------------------------
# versie 1.0.3
# --------------------------------------------------------------------------
# 15-05-2018 - wegschrijven XML tbv Riskeer toegevoegd.
# 18-06-2018 - prfl gesorteerd wegschrijven(cursor gesorteerd)
#              variabele uitvoer XML naam toegevoegd.
#              VakFC is nu ook als layer input mogelijk evt. met selectie.
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
kol          = "PRFLpunten"            # vaste kolom waar het type punt in staat
Opmkol       = "PRFL_Opmerkingen"      # de opmerkingen kolom
Uitkol       = "UIT_PRFL_Bestand"      # kolom waar het volledig path naar de prfl in kan worden weggeschreven. max. 250 anders alleen de naam
Typekol      = "TypeDijk"              # type moet groene dijk zijn damwand wordt in een andere routine speciaal voor Hydra-NL geexporteerd.

# domeinen voor controle XML invoer waarden
HBNberekenen = ['niet','norm','doorsnede']
GEKB_JN = ['true','false']
DamType = ['verticalewand','caisson','havendam']
# De benodigde kolommen voor het aanmaken van de XML.
XMLkolommen = ["OID@","SHAPE@","ID","Vaknaam","PRFL_DijkNormaal", "PRFL_KruinHgt","XML_HBNberekenen","XML_OverslagdebietBerekenen","XML_IllustratiePntInlezen",
            "XML_HBNillustratiePntInlezen","XML_OverslagDebietIllustratiePntInlezen","XML_DamGebruiken","XML_DamType",
            "XML_DamHoogte","XML_VoorlandGebruiken","XML_VerwachtingsWaarde","XML_StandaardAfwijking", "XML_Mapnaam", "HRD_Name", "UIT_XML_Bestand", Typekol]

#--------------------------------------------------------------------------------------------------
# databasedir bepalen
workspace = arcpy.Describe(VakFC).path
arcpy.env.workspace = workspace
#--
def MaakPunt(pnt,id,x,y):
    pnt.id = id
    pnt.x  = x
    pnt.y  = y

def Maakshp(uitdir,pshp):
    arcpy.AddMessage("uitvoer dir:  "+uitdir)
    arcpy.AddMessage("uitvoer shp:  "+pshp)
    arcpy.CreateFeatureclass_management(uitdir, pshp, "POINT", template="#", has_m="DISABLED", has_z="DISABLED")
    Ushp = uitdir+"/"+pshp
    arcpy.AddField_management(Ushp, "Naam", "TEXT", "", "", "25", "", "NON_NULLABLE", "NON_REQUIRED", "")
    arcpy.AddField_management(Ushp, "Bestand", "TEXT", "", "", "75", "", "NON_NULLABLE", "NON_REQUIRED", "")
    arcpy.DeleteField_management(Ushp, "ID")
    arcpy.AddField_management(Ushp, "ID", "TEXT", "", "", "25", "", "NON_NULLABLE", "NON_REQUIRED", "")
    arcpy.AddField_management(Ushp, "X0", "FLOAT", "5", "2", "", "", "NON_NULLABLE", "NON_REQUIRED", "")
    return Ushp
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
      Klijst.append(XMLcursor.fields[k])
    else:
      # sommige kolommen controleren tov domein
      if k == 6:
        if str(rij[k]) not in HBNberekenen:
          check = True
          arcpy.AddError("Waarde in kolom: "+str(XMLcursor.fields[k])+" niet juist!")
          Klijst.append(XMLcursor.fields[k])
      elif k == 7:
        if str(rij[k]) not in HBNberekenen:
          check = True
          arcpy.AddError("Waarde in kolom: "+str(XMLcursor.fields[k])+" niet juist!")
          Klijst.append(XMLcursor.fields[k])
      elif k == 8:
        if str(rij[k]) not in GEKB_JN:
          check = True
          arcpy.AddError("Waarde in kolom: "+str(XMLcursor.fields[k])+" niet juist!")
          Klijst.append(XMLcursor.fields[k])
      elif k == 9:
        if str(rij[k]) not in GEKB_JN:
          check = True
          arcpy.AddError("Waarde in kolom: "+str(XMLcursor.fields[k])+" niet juist!")
          Klijst.append(XMLcursor.fields[k])
      elif k == 10:
        if str(rij[k]) not in GEKB_JN:
          check = True
          arcpy.AddError("Waarde in kolom: "+str(XMLcursor.fields[k])+" niet juist!")
          Klijst.append(XMLcursor.fields[k])
      elif k == 11:
        if str(rij[k]) not in GEKB_JN:
          check = True
          arcpy.AddError("Waarde in kolom: "+str(XMLcursor.fields[k])+" niet juist!")
          Klijst.append(XMLcursor.fields[k])
      elif k == 12:
        if str(rij[k]) not in DamType:
          check = True
          arcpy.AddError("Waarde in kolom: "+str(XMLcursor.fields[k])+" niet juist!")
          Klijst.append(XMLcursor.fields[k])
      elif k == 13:
        if rij[k] < 0 or rij[k] > 100:
          check = True
          arcpy.AddError("Waarde in kolom: "+str(XMLcursor.fields[k])+" niet juist!")
          Klijst.append(XMLcursor.fields[k])
      elif k == 14:
        if str(rij[k]) not in GEKB_JN:
          check = True
          arcpy.AddError("Waarde in kolom: "+str(XMLcursor.fields[k])+" niet juist!")
          Klijst.append(XMLcursor.fields[k])
      elif k == 15:
        if rij[k] < 0 or rij[k] > 100:
          check = True
          arcpy.AddError("Waarde in kolom: "+str(XMLcursor.fields[k])+" niet juist!")
          Klijst.append(XMLcursor.fields[k])
      elif k == 16:
        if rij[k] < 0 or rij[k] > 100:
          check = True
          arcpy.AddError("Waarde in kolom: "+str(XMLcursor.fields[k])+" niet juist!")
          Klijst.append(XMLcursor.fields[k])
    k = k+1
  CHKlijst.append(check)
  CHKlijst.append(Klijst)
  return CHKlijst
#---
arcpy.env.overwriteOutput = True
arcpy.AddMessage("\n  >>> ----------------------------------")
arcpy.AddMessage("  >>> Wegschrijven prfl ")
arcpy.AddMessage("  >>> ----------------------------------")
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
# ----  START  ----
#--------------------------------------------------------------------------------------------------
# per vak naam uitlezen, profielnamen selecteren en lijst van maken.
kolommen = ["OID@", "SHAPE@", IDkol, Vkol, Opmkol, ruw_kol1, ruw_kol2, ruw_kol3, ruw_kol4, ruw_kol5, normaal, Typekol]
# Aantal vakken uitlezen.
waar = Typekol +" = 'groene dijk'"
countTOT = len(list(i for i in arcpy.da.SearchCursor(VakFC, kolommen)))
count = len(list(i for i in arcpy.da.SearchCursor(VakFC, kolommen, where_clause=waar)))
arcpy.AddMessage("\nAantal vakken: "+str(count)+" van "+str(countTOT)+" verwerken.")
#-------------------------
VAKlst = []
with arcpy.da.SearchCursor(VakFC, kolommen, where_clause=waar,sql_clause=(None, 'ORDER BY '+Vkol)) as cursor:
    for row in cursor:
        Pnm = "PRFL_P_"+row[2].replace('-','_')
        # XY middelpunt bepalen.
        feat = row[1]
        x = feat.positionAlongLine(0.5,True).firstPoint.X
        y = feat.positionAlongLine(0.5,True).firstPoint.Y
        mid = [x,y]
        VAKlst.append([row[2],row[3],Pnm,mid,row[4],row[5],row[6],row[7],row[8],row[9],row[10]])        
del row, cursor
#--------------------------------------------------------------------------------------------------
# lege shape aanmaken om de punten in op te slaan
Opshp = "Vak_profielpunt_GEKB_"+onaam+".shp"
Uitshp = Maakshp(odir, Opshp)
vaknr = 0
#--------------------------------------------------------------------------------------------------
for vak in VAKlst:
    FOUT1 = False   # als de benodigde variabelen niet juist zijn dan geen PRFL wegschrijven!
    vaknr = vaknr + 1
    VakID = vak[0]
    Vnaam = vak[1]
    arcpy.AddMessage("\n--------------------------------")
    arcpy.AddMessage("\nVakID: "+str(VakID))
    arcpy.AddMessage("Naam: "+str(vak[1]))
    #-- De PRFL punten FC selecteren en de punten uitlezen.
    Pshp = vak[2]
    midP = vak[3]     # middelpunt v/d lijn
    Opm  = vak[4]
    ruw1 = vak[5]
    ruw2 = vak[6]
    ruw3 = vak[7]
    ruw4 = vak[8]
    ruw5 = vak[9]
    NORMAAL = vak[10]    
    kolommen = ["SHAPE@XY", kol]
    were = kol +" LIKE '%_prfl'"
    #---------------------------------------------------------
    # check of de waarden van de uitgelezen kolommen(van het VAK) bruikbaar zijn.
    # dus ruw1-ruw5 moeten er zijn als er ook meerdere taludsegmenten zijn.
    # Dit is in de voorgaande stappen gecontroleerd dus wordt er hier vanuit gegaan dat de waarden juist zijn.
    if ruw1 >= 0.5 and ruw1 <= 1.0:
        arcpy.AddMessage("ruw1 = ok")
    else:
        arcpy.AddWarning("ruw1 = "+str(ruw1)+" = Niet ingevoerd! wordt op 1 gezet!")
        ruw1 = ruwheid
    if ruw2 >= 0.5 and ruw1 <= 1.0:
        arcpy.AddMessage("ruw2 = ok")
    else:
        arcpy.AddWarning("ruw2 = "+str(ruw2)+" = Niet ingevoerd! wordt op 1 gezet")
        ruw2 = ruwheid
    if ruw3 >= 0.5 and ruw1 <= 1.0:
        arcpy.AddMessage("ruw3 = ok")
    else:
        arcpy.AddWarning("ruw3 = "+str(ruw3)+" = Niet ingevoerd! wordt op 1 gezet")
        ruw3 = ruwheid
    if ruw4 >= 0.5 and ruw1 <= 1.0:
        arcpy.AddMessage("ruw4 = ok")
    else:
        arcpy.AddWarning("ruw4 = "+str(ruw4)+" = Niet ingevoerd! wordt op 1 gezet")
        ruw4 = ruwheid
    if ruw5 >= 0.5 and ruw1 <= 1.0:
        arcpy.AddMessage("ruw5 = ok")
    else:
        arcpy.AddWarning("ruw5 = "+str(ruw5)+" = Niet ingevoerd! wordt op 1 gezet")
        ruw5 = ruwheid        
    if NORMAAL > 0 and NORMAAL < 401:
        arcpy.AddMessage("Normaal = ok")
    else:
        arcpy.AddError("Normaal = "+str(NORMAAL)+" = Niet juist!")
        FOUT1 = True
    #---------------------------------------------------------
    # Als de FC er niet is dan vak overslaan.
    #arcpy.AddMessage("FC Pshp: "+str(Pshp))
    Pchk = arcpy.Exists(Pshp)
    #---------------------------------------------------------
    if Pchk and FOUT1 == False:
        # uitlezen.
        count = len(list(i for i in arcpy.da.SearchCursor(Pshp, kolommen, where_clause=were)))
        arcpy.AddMessage("Aantal punten: "+str(count))
        XYlijst  = []
        VOORLlst = []
        TALUDlst = []
        # -------------------------
        if count > 0:
            with arcpy.da.SearchCursor(Pshp, kolommen, where_clause=were) as cursor:
                for row in cursor:
                    xy = row[0]
                    XYlijst.append(xy)
                    Pnm = row[1]
                    #arcpy.AddMessage(Pnm)
                    # Voorland (kunnen meerdere punten zijn
                    if Pnm == 'Voorland_prfl':
                        VOORLlst.append(xy)
                    # Buitenteen (altijd 1)
                    elif Pnm == 'Buitenteen_prfl':
                        TEEN = xy
                    # Kruin (altijd 1)
                    elif Pnm == 'Buitenkruin_prfl':
                        KRUIN = xy
                    elif Pnm == 'Taludknik_prfl':
                        TALUDlst.append(xy)
            VOORLlst = sorted(VOORLlst)
            TALUDlst = sorted(TALUDlst)
            # recht talud anders behandelen als een getrapt talud.
            if len(TALUDlst) == 0:
                # Maar 2 punten en dat zijn de teen en kruin
                TALUDlst.append([TEEN[0],TEEN[1],ruw1])
                TALUDlst.append([KRUIN[0],KRUIN[1],ruw1])
            elif len(TALUDlst) < 5:
                # meerdere taludpunten
                # altijd de kruin, teen en 1 of meer taludknikpunten                
                TALUDlst.append(TEEN)
                TALUDlst = sorted(TALUDlst)
                tmpLST = []
                nr = len(TALUDlst)
                for PNT in TALUDlst:
                    # punt toevoegen incl. juiste ruwheid
                    tmpLST.append([PNT[0],PNT[1],eval("ruw"+str(nr))])
                    nr -= 1                
                tmpLST.append([KRUIN[0],KRUIN[1],ruw1])   # ruwheid is altijd de 1e maar doet er niet toe voor Ringtoets.
                TALUDlst = sorted(tmpLST)
            else:
                arcpy.AddError(" Er zijn meer dan 5 taludknikpunten! Verwijder of voeg punt(en) toe!")
                FOUT1 = True
            #-----
            if FOUT1 == False:    
                XYlijst = sorted(XYlijst)
                #---
                # X0 bepalen = begin profiel tot referentielijn(X=0)
                X0 = int(XYlijst[0][0])
                oprfl_naam = "PRFL_"+Vnaam+".prfl"
                # Ook de uitvoer prfl bestandsnaam en path wegschrijven. Indien > 250 kar dan alleen bestandsnaam
                were = IDkol+" = '"+VakID+"'"
                kolommen = [IDkol,Uitkol,"X0"]
                BestNaam = os.path.join(odir,oprfl_naam)
                if len(BestNaam) > 250:
                    BestNaam = oprfl_naam                
                with arcpy.da.UpdateCursor(VakFC, kolommen, where_clause=were) as Updcursor:
                    for row in Updcursor:
                        row[1] = BestNaam
                        row[2] = X0
                        # het vak updaten.
                        Updcursor.updateRow(row)
                #---
                # Punt toevoegen aan shapefile en prfl tekstfile schrijven.
                rows = arcpy.InsertCursor(Uitshp)
                pnt = arcpy.geoprocessing.gp.createobject("point")
                irow = rows.newRow()
                pnr = vaknr
                MaakPunt(pnt, pnr, midP[0], midP[1])
                irow.shape = pnt
                irow.setValue("ID", vak[0])
                irow.setValue("X0", X0)
                irow.setValue("Bestand", oprfl_naam)
                irow.setValue("Naam", Vnaam)
                rows.insertRow(irow)
                #----
                # Nu *prfl maken
                # uitvoer txt file killen als ie al bestaat.
                try:
                    arcpy.Delete_management(odir+"/"+oprfl_naam, "File")
                except:
                    print("")

                # Open prfl file
                ll = open(odir+"/"+oprfl_naam, "w")
                ll.write("VERSIE\t4.0\n")
                ll.write("\n")
                ll.write("ID\t" + str(VakID) + "\n")
                ll.write("\n")
                ll.write("RICHTING\t" + str(round(NORMAAL,2)) + "\n")
                ll.write("\n")
                ll.write("DAM\t0\n")
                ll.write("\n")
                ll.write("DAMHOOGTE\t0\n")
                ll.write("\n")
                Nv = len(VOORLlst) + 1
                ll.write("VOORLAND\t" + str(Nv) + "\n")
                for pp in VOORLlst:             
                    ll.write(str('{:,.3f}'.format(pp[0])) +"\t" + str('{:,.3f}'.format(pp[1])) + "\t"+ str(ruwheid) + "\n")
                # Als laatste voorland op de teen aan laten sluiten
                ll.write(str('{:,.3f}'.format(TEEN[0])) +"\t"+ str('{:,.3f}'.format(TEEN[1])) +"\t"+ str(ruwheid) + "\n")
                ll.write("\n")
                ll.write("DAMWAND\t0\n")
                ll.write("\n")
                Kv = len(TALUDlst)
                ll.write("KRUINHOOGTE\t" + str(round(KRUIN[1],2)) + "\n")
                ll.write("\n")
                ll.write("DIJK\t"+str(Kv)+"\n")
                for KRNpnt in TALUDlst:
                    ll.write(str('{:,.3f}'.format(KRNpnt[0])) +"\t"+ str('{:,.3f}'.format(KRNpnt[1])) +"\t"+ str('{:,.3f}'.format(KRNpnt[2])) + "\n")
                ll.write("\n")
                ll.write("MEMO\n")
                ll.write("\nWaterschap Rijn en IJssel\n\n")
                ll.write("Profiel gegenereed op:\t")
                ll.write("'" + str(tijd) + "'\n")
                ll.write("Vaknaam:\t\t")
                ll.write(str(Vnaam)+"\n")            
                ll.write("Opmerkingen:\t\t")
                ll.write(str(Opm)+"\n")
                ll.flush()
                ll.close()
                #----
                arcpy.AddMessage("\n--  Resultaten weggeschreven naar:  \n--  " + oprfl_naam + "\n")
        else:
            arcpy.AddError("geen prfl punten!!")
arcpy.AddMessage("--------------------------------\n")
#---------------------------------------------------------------------------------------------------------------------------------------
#***************************************************************************************************************************************
# XML aanmaken
#***************************************************************************************************************************************
#---------------------------------------------------------------------------------------------------------------------------------------
arcpy.AddMessage("  >>> ----------------------------------")
arcpy.AddMessage("  >>> Wegschrijven XML ")
arcpy.AddMessage("  >>> ----------------------------------")
# Voor het aanmaken van de XML
# per vak naam uitlezen, profielnamen selecteren en lijst van maken.
# Aantal vakken uitlezen.
count = len(list(i for i in arcpy.da.SearchCursor(VakFC, XMLkolommen, where_clause=waar)))
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
with arcpy.da.UpdateCursor(VakFC, XMLkolommen, where_clause=waar, sql_clause=(None, 'ORDER BY XML_Mapnaam,'+Vkol)) as XMLcursor:   # sorteren op Mapnaam en ID
  for XMLrow in XMLcursor:    
    FOUT = False   # als de benodigde variabelen niet juist zijn dan niet in de XML wegschrijven!
    arcpy.AddMessage("\n--------------------------------")
    arcpy.AddMessage("VakID: "+str(XMLrow[2]))
    arcpy.AddMessage("Naam: "+str(XMLrow[3]))
    #---------------------------------------------------------
    # kolomwaarden controleren.
    control = controleerVak(XMLrow)
    FOUT = control[0]
    Klijst = control[1]
    #---------------------------------------------------------
    # Ook even kijken of er wel een prfl van het vak bestaat! Zo niet dan alleen melden.
    Pfchk = False
    were = IDkol +" = '"+str(XMLrow[2])+"'"
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
      if Mapnm != XMLrow[17]:
        mapEL  = ET.SubElement(confEL,"map")
        mapEL.set("naam", str(XMLrow[17]))
        Mapnm = str(XMLrow[17])

      arcpy.AddMessage("berekening aanmaken...")
      
      # de berekening
      berekeningEL = ET.SubElement(mapEL,"berekening")
      berekeningEL.set("naam", str(XMLrow[3]))
      hrloc = ET.SubElement(berekeningEL, "hrlocatie")
      hrloc.text = str(XMLrow[18])
      hrd = ET.SubElement(berekeningEL, "dijkprofiel")
      hrd.text = str(XMLrow[2])
      
      # **** Kan worden uitgezet wordt gewoon van profiel overgenomen! ****
      profsch = ET.SubElement(berekeningEL, "orientatie")
      profsch.text = str(round(XMLrow[4],2))
      intr = ET.SubElement(berekeningEL, "dijkhoogte")
      intr.text = str(round(XMLrow[5],2))
      
      uittr = ET.SubElement(berekeningEL, "illustratiepunteninlezen")
      uittr.text = str(XMLrow[8])
      ond = ET.SubElement(berekeningEL, "hbnillustratiepunteninlezen")
      ond.text = str(XMLrow[9])
      onds = ET.SubElement(berekeningEL, "overslagdebietillustratiepunteninlezen")
      onds.text = str(XMLrow[10])
      onds = ET.SubElement(berekeningEL, "hbnberekenen")
      onds.text = str(XMLrow[6])
      onds = ET.SubElement(berekeningEL, "overslagdebietberekenen")
      onds.text = str(XMLrow[7])

      # **** Kan worden uitgezet wordt gewoon van profiel overgenomen! ****
      #-- Golfreductie --
      sto1 = ET.SubElement(berekeningEL, "golfreductie")
      dg = ET.SubElement(sto1, "damgebruiken")
      dg.text = str(XMLrow[11])
      verw = ET.SubElement(sto1, "damtype")
      verw.text = str(XMLrow[12])
      sd = ET.SubElement(sto1, "damhoogte")
      sd.text = str(round(XMLrow[13],2))
      vrl = ET.SubElement(sto1, "voorlandgebruiken")
      vrl.text = str(XMLrow[14])
      
      #-- Stochasten --
      sto = ET.SubElement(berekeningEL, "stochasten")
      sto1 = ET.SubElement(sto, "stochast")
      sto1.set("naam","overslagdebiet")                 # bij gekb altijd overslagdebiet.
      verw = ET.SubElement(sto1, "verwachtingswaarde")
      verw.text = str(XMLrow[15])
      sd = ET.SubElement(sto1, "standaardafwijking")
      sd.text = str(XMLrow[16])
      #--
      # Naam van de XML waarin het profiel is weggeschreven aan het vak koppelen. kolom=UIT_XML_Bestand
      XMLrow[19] = os.path.join(odir,uitXML)
      XMLcursor.updateRow(XMLrow)
    else:
      if not Pfchk:
          arcpy.AddWarning("\nVak overgeslagen omdat er geen PRFL voor is aangemaakt!")
      else:
          arcpy.AddError("\nxx Vak overgeslagen te weinig informatie!")
          arcpy.AddError("xx De volgende kolommen zijn niet of niet juist ingevuld: \n"+str(Klijst))
arcpy.AddMessage("\n--------------------------------")
# Nu de XML mooi opmaken
indent(confEL)
# wegschrijven naar XML file
tree = ET.ElementTree(confEL)
tree.write(odir+"/"+uitXML, xml_declaration=True, encoding='utf-8', method="xml")
arcpy.AddMessage("\n--  XML weggeschreven naar:  \n--  " + uitXML)
#--------------------------------------------------------------------------------------------------
# Als laatste de vakken als shape file in de uitvoer directory zetten.
# eerst de selectie van de vakken halen omdat Ringtoets altijd het gehele Normtraject nodig heeft.
try:
    arcpy.SelectLayerByAttribute_management(VakFC, "CLEAR_SELECTION")
except:
    print ""
arcpy.CopyFeatures_management(in_features=VakFC, out_feature_class=odir+"/Vakindeling_GEKB_"+onaam+".shp")
#--------------------------------------------------------------------------------------------------
arcpy.AddMessage("\n--------------------------------")
arcpy.AddMessage("\n  >>>  KLAAR!  <<<")
