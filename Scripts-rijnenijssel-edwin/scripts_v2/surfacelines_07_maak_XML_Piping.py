# --------------------------------------------------------------------------
# Aanmaken Piping berekening XML voor Riskeer
# ing. H.E.J. Nieuwland - mei 2018
# --------------------------------------------------------------------------
# versie 1.0.1
# --------------------------------------------------------------------------
# Er is altijd maar 1 segment waarin het betreffende profiel ligt.
# En dan x keer de bij het segment horende 1D profielen.
# 20180529 - update met % voor scenario ook uit soil lezen.
# --------------------------------------------------------------------------
import string, os, sys, locale, arcpy
from xml.etree import ElementTree as ET
# INPUT
VakFC    = sys.argv[1]         # Vakindeling FC
SoilIN   = sys.argv[2]         # Dsoil bestand
lnFC     = sys.argv[3]         # PWK_GEO_PROFIELLIJNEN
LnmKol   = "PROFIELNAAM"       # kolom met profielnaam
Tkol     = "TYPE"              # Binnentalud of Buitentalud voor samenvoegen
Uitdir   = sys.argv[4]         # Uitvoer directory voor de XML
uitXML   = sys.argv[5]+".xml"  # Naam uit XML
#---
# databasedir bepalen
workspace = arcpy.Describe(VakFC).path
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True
arcpy.AddMessage("  >>> ----------------------------------")
arcpy.AddMessage("  >>> Wegschrijven XML(Piping) vanaf vakindeling ")
arcpy.AddMessage("  >>> ----------------------------------")
#---------------------------------------------------------
#---------------------------------------------------------
# ----  START
#---------------------------------------------------------
#---------------------------------------------------------
def LeesSOIL(Soil):
    arcpy.AddMessage("  >>> ----------------------------------")
    arcpy.AddMessage("  >>> Uitlezen: "+Soil)
    arcpy.AddMessage("  >>> ----------------------------------")
    #---------------------------------------------------------
    # ----  START ----
    #---------------------------------------------------------
    # Uit te lezen tabellen en structuur uitleg:
    # 
    # Hier kijken welk ME_ID is Piping
    # tabel: main.Mechanism uit te lezen kolommen: ME_ID en ME_Name (daar waar deze  = Piping die gebruiken)
    #
    # Dan hier kijken welke Segmenten bij Piping horen
    # tabel: main.Segment uit te lezen kolommen: SE_ID, ME_ID, SSM_ID, SE_Name (
    # 
    # in onderstaande 2 tabellen de Naam en het aantal 1D profielen uit lezen.
    # tabel: main.StochasticSoilProfile uit te lezen kolommen: SSM_ID en SP1D_ID
    # tabel: main.StochasticSoilModel uit te lezen kolommen: SSM_ID en SSM_Name(is de ondergrondmodelnaam)
    #
    # In onderstaande tabel de namen van de profielen uitlezen.
    # tabel: main.SoilProfile1D uit te lezen kolommen: SP1D_ID en SP1D_Name(is de segment naam)
    #
    # Nog geen foutafhandeling ingebouwd om te kijken of het wel een sqlite bestand is
    #
    import sqlite3
    conn = sqlite3.connect(Soil)
    cursor = conn.cursor()
    #------------------
    # Lege lijnen shape aanmaken voor 
    lijnID = 0
    LijnLijst = arcpy.Array()
    # de uitvoer FC
    oSoil_ln = "Seg_"+arcpy.Describe(Soil).file.replace(".","_").replace("-","_")
    try:
        arcpy.CreateFeatureclass_management(out_path=workspace, out_name=oSoil_ln, geometry_type="POLYLINE", template="", has_m="DISABLED", has_z="DISABLED", spatial_reference="PROJCS['RD_New',GEOGCS['GCS_Amersfoort',DATUM['D_Amersfoort',SPHEROID['Bessel_1841',6377397.155,299.1528128]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Double_Stereographic'],PARAMETER['False_Easting',155000.0],PARAMETER['False_Northing',463000.0],PARAMETER['Central_Meridian',5.38763888888889],PARAMETER['Scale_Factor',0.9999079],PARAMETER['Latitude_Of_Origin',52.15616055555555],UNIT['Meter',1.0]];-30515500 -30279500 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision")
    except:
        print "is er al"
    UitSoil = workspace+"/"+oSoil_ln
    try:
        arcpy.AddField_management(UitSoil, "SE_ID", "SHORT")
    except:
        arcpy.AddError("Kolom SE_ID bestaat al!")
    try:
        arcpy.AddField_management(UitSoil, "SE_NAME", "TEXT", "", "", 100)
    except:
        arcpy.AddError("Kolom SE_NAME bestaat al!")
    #------------------
    # cursor openen
    insert_cursor = arcpy.da.InsertCursor(UitSoil,["SHAPE@","SE_ID","SE_NAME"])
    #------------------
    MEid = 0                  # Het id van Piping komt in deze variabele
    cursor.execute("SELECT ME_ID, ME_Name FROM Mechanism WHERE ME_Name = 'Piping'")
    for row0 in cursor.fetchall():
        MEid = row0[0]
    del row0
    #------------------
    StochastModel = []          # hier komt het eindmodel in.
    cursor.execute("SELECT SE_ID, ME_ID, SSM_ID, SE_Name FROM Segment WHERE ME_ID = '"+str(MEid)+"' ORDER BY SSM_ID")
    for row1 in cursor.fetchall():
        SSMlijst = []             # De lijst met nummer en modelnamen
        SSMlijst.append(row1[0])
        SSMid = row1[2]
        SEid = row1[0]
        SEnaam = row1[3]
        #------------------
        # de lijn uittekenen
        LijnLijst = arcpy.Array()
        cursor.execute("SELECT SE_ID, Xworld, Yworld FROM SegmentPoints WHERE SE_ID = '"+str(SEid)+"' ORDER BY SEGP_ID")
        for XYrow in cursor.fetchall():
            P = arcpy.Point(XYrow[1],XYrow[2])
            LijnLijst.add(P)        
        polyline = arcpy.Polyline(LijnLijst)
        #-- wegschrijven
        insert_cursor.insertRow((polyline,float(SEid),SEnaam))
        LijnLijst.removeAll()
        #------------------
        cursor.execute("SELECT SSM_ID, SSM_Name FROM StochasticSoilModel  WHERE SSM_ID = '"+str(SSMid)+"'")
        for row2 in cursor.fetchall():
            SSMnaam = row2[1]
        SP1Dlijst = []            # De lijst met de 1D profielen per segment
        cursor.execute("SELECT SSM_ID, SP1D_ID, Probability FROM StochasticSoilProfile WHERE SSM_ID = '"+str(SSMid)+"' ORDER BY SP1D_ID")
        for row3 in cursor.fetchall():
            SP1D = row3[1]
            SP1Dk = row3[2] * 100   # de kans binnen het scenario 
            cursor.execute("SELECT SP1D_ID, SP1D_Name FROM SoilProfile1D  WHERE SP1D_ID = '"+str(SP1D)+"'")
            for row4 in cursor.fetchall():
                SP1Dlijst.append([row4[1],SP1Dk])  # Kans meenemen
        StochastModel.append([SSMnaam,SP1Dlijst])
    cursor.close()
    del insert_cursor
    #---
    return(StochastModel,UitSoil)
#---------------------------------------------------------
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

#---------------------------------------------------------
def afstandToSoil(lijn,SoilFC):
    arcpy.AddMessage("  >>> Soil segment selecteren")
    SEGlijst = []
    with arcpy.da.SearchCursor(SoilFC, ["SHAPE@", "SE_ID", "SE_NAME"]) as SEGcursor:
        for seg in SEGcursor:
            dP = seg[0].disjoint(lijn)
            if not dP:
                SEGlijst.append([seg[1],seg[2]])
    del SEGcursor
    #---
    return(SEGlijst)
#--------------------------------------------------------
def SelecteerReprprof(Rprof):
    arcpy.AddMessage("  Representatief profiel: "+str(Rprof))    
    # 2 proflijn selecteren uit PWK_GEO_PROFIELLIJNEN zijn 2 stukken eerst samenvoegen.
    waar = LnmKol + " = '"+Rprof+"'"
    aantal = len(list(i for i in arcpy.da.SearchCursor(lnFC, ["SHAPE@", LnmKol, Tkol], where_clause=waar)))
    if aantal == 0: 
        arcpy.AddWarning("  !! Representatief profiel niet gevonden! Vak wordt overgeslagen.")
        DeLijn = False
    elif aantal >= 1: # 1 of 2 lijnstukken. 
        with arcpy.da.SearchCursor(lnFC, ["SHAPE@", LnmKol, Tkol], where_clause=waar) as LNcursor:            
            for Lrow in LNcursor:
                if Lrow[2] == "Binnentalud":
                    Lbin = Lrow[0]
                elif Lrow[2] == "Buitentalud":
                    Lbui = Lrow[0]
            # De dwarsprofiel lijn
            DeLijn = Lbui.union(Lbin)
    return(DeLijn)
#--------------------------------------------------------
# --- START ---
#--------------------------------------------------------
# Eerst *.soil inlezen, segmentnaam en 1D profielnamen vinden.
verwerkSoil = LeesSOIL(SoilIN)
SoilLijst = verwerkSoil[0]
SoilLN = verwerkSoil[1]
arcpy.AddMessage("  >>> Soil bestand uitgelezen/n")
#arcpy.AddMessage(SoilLijst)
#--------------------------------------------------------
# per vak naam uitlezen, profielnamen selecteren en lijst van maken.
kolommen = ["OID@","SHAPE@","ID","Vaknaam","HRD_Name","UIT_CSV_Bestand","XML_Mapnaam","XML_intredepunt","XML_uittredepunt",
            "XML_VerwachtingswaardePolderpeil","XML_StandaardafwijkingPolderpeil","XML_VerwachtingswaardeDempingsfactor",
            "XML_StandaardafwijkingDempingsfactor","REPROF_NAAM"]

# Aantal vakken uitlezen.
count = len(list(i for i in arcpy.da.SearchCursor(VakFC, kolommen)))
arcpy.AddMessage("  Aantal vakken: "+str(count))
#-------------------------
#-- De XML
arcpy.AddMessage("  XML: "+uitXML+" aanmaken...")

# Deel 1 XML aanmaken
confEL = ET.Element("configuratie")

# Nu door de vakken loopen om de losse berekeningen 
VAKlst = []
vaknr = 0
Mapnm = 'leeg'
with arcpy.da.SearchCursor(VakFC, kolommen, sql_clause=(None, 'ORDER BY XML_Mapnaam, Vaknaam')) as cursor:   # sorteren op Mapnaam en Vaknaam
  for row in cursor:    
    FOUT = False   # als de benodigde variabelen niet juist zijn dan niet in de XML wegschrijven!
    vaknr = vaknr + 1
    VakID = row[2]
    Vnaam = row[3]
    Mapnaam = row[6]
    ReprP = row[13]
    arcpy.AddMessage("\n--------------------------------")
    arcpy.AddMessage("  VakID: "+str(VakID))
    arcpy.AddMessage("  Naam: "+str(Vnaam))
    
    if ReprP != None:
        arcpy.AddMessage("  Repr. Profiel: "+str(ReprP))
        #---------------------------------------------------------
        rprof = str(ReprP)
        rlijn = SelecteerReprprof(rprof)
        #---------------------------------------------------------
        # Kruising Soil segmenten met dwarsprofiel bepalen. 
        SoilSegLijst = afstandToSoil(rlijn,SoilLN)
        #---------------------------------------------------------
        # Segmenten en bijbehorende 1D profielen selecteren uit de SoilLijst
        for soil in SoilLijst :
            for soilseg in SoilSegLijst:
                if soil[0] == soilseg[1] :
                    SEGM = soil[0]
                    SEG1Dlijst = soil[1]
        arcpy.AddMessage("  Soil Segment: "+str(SEGM))
        #---------------------------------------------------------
        if Mapnaam == None:
            Mapnaam = "WRIJ_berekeningen"
        if Mapnm != Mapnaam:
            mapEL1  = ET.SubElement(confEL,"map")
            mapEL1.set("naam", str(Mapnaam))
            Mapnm = str(Mapnaam)
            
        # altijd map met de 1D profielen
        mapEL  = ET.SubElement(mapEL1,"map")
        mapEL.set("naam", Vnaam)
        # de berekening
        arcpy.AddMessage("  >>> berekening aanmaken...")
        # per profiel = vak een map aanmaken en daar alle bij het vak horende segmenten en 1D profielen aan toe voegen.
        for D1 in SEG1Dlijst:
            arcpy.AddMessage("  1D: "+str(D1[0]))
            berekeningEL = ET.SubElement(mapEL,"berekening")
            berekeningEL.set("naam", str(ReprP)+" "+ D1[0])
            hrd = ET.SubElement(berekeningEL, "hrlocatie")
            hrd.text = str(row[4])
            profsch = ET.SubElement(berekeningEL, "profielschematisatie")
            profsch.text = str(ReprP)
            # intredepunt moet voor uittredepunt liggen
            # Melding Ringtoets: Een waarde van '-10' als intredepunt is ongeldig.
            # Het gespecificeerde punt moet op het profiel liggen (bereik [0.0, 155.99]).
            # Berekening '48-1_dp4+32 Segment_48007_1D1' is overgeslagen.
            if row[7] > row[8]:
                arcpy.AddError("  Intredepunt moet voor uittredepunt liggen!\n  Controleer eerst de waarden in XML_intredepunt en XML_uittredepunt.\n  EXIT...\n")
                sys.exit()
            intr = ET.SubElement(berekeningEL, "intredepunt")
            intr.text = str(row[7])
            uittr = ET.SubElement(berekeningEL, "uittredepunt")
            uittr.text = str(row[8])
            ond = ET.SubElement(berekeningEL, "ondergrondmodel")
            ond.text = SEGM
            onds = ET.SubElement(berekeningEL, "ondergrondschematisatie")
            onds.text = D1[0]
            #--
            sto = ET.SubElement(berekeningEL, "stochasten")
            sto1 = ET.SubElement(sto, "stochast")
            sto1.set("naam","polderpeil")
            verw = ET.SubElement(sto1, "verwachtingswaarde")
            verw.text = str(row[9])
            sd = ET.SubElement(sto1, "standaardafwijking")
            sd.text = str(row[10])
            sto2 = ET.SubElement(sto, "stochast")
            sto2.set("naam","dempingsfactor")
            verw2 = ET.SubElement(sto2, "verwachtingswaarde")
            verw2.text = str(row[11])
            sd2 = ET.SubElement(sto2, "standaardafwijking")
            sd2.text = str(row[12])
            #-- Altijd invoeren is uitgelezen uit Soil.
            scenEL = ET.SubElement(berekeningEL, "scenario")
            gebr = ET.SubElement(scenEL, "gebruik")
            gebr.text = 'true'
            gebr = ET.SubElement(scenEL, "bijdrage")
            gebr.text = str(D1[1])
            #--
    else:
        arcpy.AddWarning("  Vak heeft geen representatief profiel! Wordt nu overgeslagen.")
del row, cursor

arcpy.AddMessage("\n--------------------------------")
arcpy.AddMessage(" Nu XML opmaken en wegschrijven...")

# Nu de XML mooi opmaken
indent(confEL)
uff = ET.tostring(confEL,encoding='UTF-8')

# wegschrijven naar XML file
tree = ET.ElementTree(confEL)
tree.write(Uitdir+"/"+uitXML, xml_declaration=True, encoding='utf-8', method="xml")

arcpy.AddMessage("\n  >>>  KLAAR!  <<<")
