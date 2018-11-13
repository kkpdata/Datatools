# --------------------------------------------------------------------------
# Wegschrijven profielen per vak tbv *.prfl tbv Ringtoets
# Witteveen+Bos
# ing. H.E.J. Nieuwland - november 2017
# --------------------------------------------------------------------------
# versie 1.0.6
# --------------------------------------------------------------------------
# mrt 2018 Vaknaam ook uitlezen (VAK) en als naam van de groeplayer toepassen.
# DT_Zspot toegevoegd bij Stats
# 20180405 Sorteren van de searchcursor
# 20180411 kopie van prfl vakken nu altijd vanaf de FC niet de layer.
# 20180417 HRD locaties toevoegen aan vak obv middelpunt
# 20180501 Statistics van 1 vak werken niet goed. Nu gewijzigd en vooraf statistics bepaald en mbv array in de cursor updaten aan het vak.
# 20180711 toevoegen van kolommen eruit gehaald en naar stap 1 aanmaken vakkenbestand gehaald. Normaal kolom heet nu Mediaan..
# 20180815 De popup die verschijnt bij al bestaande profielen verwijderd.
# 20180822 Damwand optie ingebouwd obv kolom TypeDijk.
# --------------------------------------------------------------------------
import string, os, sys, locale, arcpy, pythonaddins
from time import strftime  
tijd = strftime("%m-%d-%Y %H:%M:%S")
arcpy.SetProgressor("step")

# INPUT
VakFC       = sys.argv[1]    # Vakken FC
IDkol       = "ID"           # Kolom met id vak Dit is de unieke koppeling tussen vak en prfl file. ID in beide moet gelijk zijn.
VAKkol      = "Vaknaam"      # Kolom met vaknaam voor de naam van de grouplayer
HRDkol      = "HRD_Name"     # Kolom waar de HRD naam in moet komen.
P10FC       = sys.argv[2]    # PWK punten op de lijn FC
Pkol        = "PROFIELNAAM"  # Naam van het profiel uit FME
ppFC        = sys.argv[3]    # profielpunten FC
plFC        = sys.argv[4]    # profiellijnen FC
HRDfc       = sys.argv[5]    # HRD locaties
DELL        = sys.argv[6]    # Als er al profiellen zijn dan deze verwijderen. (true) anders false of #
HRDkol_org  = "Name"         # kolom in HRD bestand met de naam van de HRD locatie
Typekol     = "TypeDijk"     # type groene dijk of damwand 
GRPlay      = os.path.dirname(__file__)+"/GroupVAK.lyr" # lege group layer voor de profielen.
lay1gd      = os.path.dirname(__file__)+"/PRFL punten.lyr"
lay1dw      = os.path.dirname(__file__)+"/PRFL Damwand punten.lyr"
lay2        = os.path.dirname(__file__)+"/Kenmerkende punten.lyr"
lay3        = os.path.dirname(__file__)+"/Profpunten.lyr"
lay4        = os.path.dirname(__file__)+"/Proflijnen_prfl.lyr"
Conkol      = "GebruikVoorDWP"   # in deze kolom kan men aangeven of het profiel wel(1) of niet(9) moet worden meegenomen
#---
# variabele DELL naar boolean
if DELL == 'true':
    DELL = True
else:
    DELL = False
arcpy.env.overwriteOutput = True
arcpy.AddMessage("  >>> ----------------------------------")
arcpy.AddMessage("  >>> Wegschrijven profielpunten per vak ")
arcpy.AddMessage("  >>> ----------------------------------\n")
#---------------------------------------------------------
#---------------------------------------------------------
# ----  START ----
#---------------------------------------------------------
arcpy.AddMessage("Vakken: \n"+VakFC)
arcpy.AddMessage("Profielpunten: \n"+ppFC)
# databasedir bepalen
workspace = os.path.dirname(ppFC)
if [any(ext) for ext in ('.gdb', '.mdb', '.sde') if ext in os.path.splitext(workspace)]:
    workspace = workspace
else:
    workspace = os.path.dirname(workspace)
arcpy.env.workspace = workspace
# Feature Dataset aanmaken voor de FC's per vak
oDS = workspace+"/PRFL_DATA"
if not arcpy.Exists(oDS):
    arcpy.CreateFeatureDataset_management(workspace, "PRFL_DATA")
    arcpy.AddMessage("Uitvoer Dataset:  PRFL_DATA aangemaakt!")
else:
    arcpy.AddMessage("Bestaande uitvoer Dataset:  PRFL_DATA gebruiken!")
#---------------------------------------------------------
# 1 vaknaam koppelen aan dwarsprofielpunten.
# Create a new fieldmappings and add the two input feature classes.
fieldmap = arcpy.FieldMappings()
fieldmap.addTable(P10FC)
fieldmap.addTable(VakFC)
arcpy.SpatialJoin_analysis(target_features=P10FC, join_features=VakFC, out_feature_class="xxProfPnt0", join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_COMMON", field_mapping=fieldmap, match_option="CLOSEST", search_radius="2 Meters")
fieldmap.removeAll()
#---------------------------------------------------------
# Nu statestieken voor het toetsvak bepalen. gem taluds, laagste max kruin, gem max kruin, gem zetting, gem dijknormaal
Stats="Z_MAX_DTM MIN;DT_Zspot MEAN;Z_MAX_DTM MEAN"
arcpy.Statistics_analysis(in_table="xxProfPnt0", out_table="xxProfPnt_Statistics", statistics_fields=Stats, case_field=IDkol)
#--
KOLlijst = [IDkol,"MIN_Z_MAX_DTM","MEAN_Z_MAX_DTM","MEAN_DT_Zspot"]
StatsLijst = []
with arcpy.da.SearchCursor("xxProfPnt_Statistics", KOLlijst) as Statscursor:
    for Stats in Statscursor:
        StatsLijst.append([Stats[0],round(Stats[1],3),round(Stats[2],3),round(Stats[3],3)])
del Stats, Statscursor

# Indien nog niet aanwezig: Kolommen toevoegen aan het vakken bestand
del KOLlijst[0]   # kolom ID verwijderen uit de lijst.
# kolom MEDIAN_DijkNormaal toevoegen als een LONG ipv DOUBLE.
try:
    arcpy.AddField_management(VakFC, "MEDIAN_DijkNormaal", "LONG")
except:
    arcpy.AddError("Kolom (MEDIAN_DijkNormaal) bestaat al!")
kolommen = ["OID@", "SHAPE@LENGTH", IDkol, VAKkol, "SHAPE@", HRDkol, "MEDIAN_DijkNormaal"]              # voor de updatecursor
for kk in KOLlijst:
    kolommen.append(kk)  # ook de stats kolommen toevoegen zodat we ze verderop kunnen updaten
    try:
        arcpy.AddField_management(VakFC, kk, "DOUBLE")
    except:
        arcpy.AddError("Kolom ("+str(kk)+") bestaat al!")
kolommen.append(Typekol)
#---------------------------------------------------------
# Niet alle profielen meenemen. Zie kolom GebruikVoorDWP als deze niet 1 is dan ook niet meenemen.
arcpy.Select_analysis(in_features="xxProfPnt0", out_feature_class="xxProfPnt", where_clause=Conkol+" = 1")
#---------------------------------------------------------
#---------------------------------------------------------
# 2 dan per vak naam uitlezen, profielnamen selecteren en lijst van maken.
# Aantal vakken uitlezen.
count = len(list(i for i in arcpy.da.SearchCursor(VakFC, kolommen)))
arcpy.AddMessage("Aantal vakken: "+str(count))
arcpy.SetProgressor("step", "Vak 0 van "+str(count)+" verwerken...", 0, count, 1)
# -------------------------
# Lijst maken met alle HRD punten om later te gebruiken en obv middelpunt te koppelen aan het vak
HRDpntLijst = []
HRDkolommen = ["OID@", "SHAPE@", HRDkol_org]
with arcpy.da.SearchCursor(HRDfc, HRDkolommen) as HRDcursor:
    for H in HRDcursor:
        HRDpntLijst.append([H[0],H[1],H[2]])
del H, HRDcursor
spatial_ref = arcpy.Describe(HRDfc).spatialReference
#---------------------------------------------------------
#-- Nu door de vakken loopen. 
#---------------------------------------------------------
#---------------------------------------------------------
ss = "ORDER BY "+VAKkol+" DESC"
teller = 0
with arcpy.da.UpdateCursor(VakFC, kolommen, sql_clause=(None,ss)) as cursor:
    for row in cursor:        
        arcpy.SetProgressorLabel("Vak " + str(teller)+" van "+str(count)+ " verwerken...")
        arcpy.SetProgressorPosition(teller)
        arcpy.AddMessage("--------------------------")
        arcpy.AddMessage("\nVakID: "+str(row[2]))
        ID = row[2].replace('-','_')
        arcpy.AddMessage("\nVaknaam: "+str(row[3]))   #  gewijzigd 27mrt2018
        VAK = row[3]
        VakType = row[10]       # kijken of vak groene dijk is of damwand
        arcpy.AddMessage("Vak type: "+str(VakType))
        if VakType == "damwand":            
            lay1 = lay1dw
        else:
            lay1 = lay1gd        
        # Nu profielpunten selecteren
        were = IDkol+" = '"+str(row[2])+"'"
        # Door de punten loopen en PROFIELNAAM in lijst zetten.
        profs = []
        waar = ""
        nn = 0
        with arcpy.da.SearchCursor("xxProfPnt", [Pkol], where_clause=were) as cursor2:
            for row2 in cursor2:
                nn = nn + 1
                profs.append(row2[0])
                if nn == 1:
                    waar = Pkol+" = '"+row2[0]+"'"
                else:
                    waar = waar+" or "+Pkol+" = '"+row2[0]+"'"
            del cursor2
        #---------------------------------------------------------
        # Alleen als er profielnamen zijn geselecteerd dan verder.
        if waar <> "":
            # 3 alle profielen selecteren en wegschrijven.
            Pnm = "Pvak_"+ID
            uitFCp = oDS+"/"+Pnm
            # Lijnen
            Lnm = "Lvak_"+ID
            uitFCl = oDS+"/"+Lnm
            # PRFL punten lege FC aanmaken obv profielpunten
            PPnm = "PRFL_P_"+ID
            uitFCpp = oDS+"/"+PPnm
            # de uitgetekende PRFL lijn indien men al verder is gegaan met het betreffende ID.
            PRFL_ln = oDS+"/PRFL_lijn_"+ID          # LET OP naam is gelijk aan die uit script 5 Maak PRFL lijn
            #--
            PRFLwaar = Pkol+" = 'niets_selecteren'"
            vraag = "Geen"
            if DELL:
                arcpy.AddWarning("verwijderen! xxx")
                try:
                    arcpy.Delete_management(uitFCp)
                except:
                    print 'x'
                try:
                    arcpy.Delete_management(uitFCl)
                except:
                    print 'x'
                # Als de prfl al is uitgetekend dan deze ook verwijderen
                try:
                    arcpy.Delete_management(PRFL_ln)
                except:
                    print 'x'
            # als FC al wel bestaat en DELL=False
            if arcpy.Exists(uitFCp)or arcpy.Exists(uitFCl):
                arcpy.AddWarning("bestaat...")
                vraag = "No"
            #--
            if DELL or (vraag == "Geen"):
                # FC aanmaken                
                # prfl lege fc
                # als er al eens prfl punten zijn ingetekend voor het betreffende VakID dan deze niet deleten
                # Gebruiker kan zelf bepalen of hij deze moet vernieuwen.
                if arcpy.Exists(uitFCpp):
                    arcpy.AddMessage(PPnm + " bestaat al. Wordt niet verwijderd!\nControleer zelf de bruikbaarheid van de PRFL punten!")
                else:
                    arcpy.AddMessage(PPnm + " aanmaken")
                    arcpy.MakeFeatureLayer_management(in_features=ppFC, out_layer="prflp_Lay", where_clause=PRFLwaar)
                    arcpy.CopyFeatures_management(in_features="prflp_Lay", out_feature_class=uitFCpp)
                #-- prof punten
                arcpy.AddMessage("Selecteren profielpunten...")
                arcpy.AddMessage(uitFCp)
                arcpy.MakeFeatureLayer_management(in_features=ppFC, out_layer="pp_Lay", where_clause=waar)
                arcpy.CopyFeatures_management(in_features="pp_Lay", out_feature_class=uitFCp)
                #-- prof lijnen
                arcpy.AddMessage("Selecteren profiellijnen...")
                arcpy.AddMessage(uitFCl)
                arcpy.MakeFeatureLayer_management(in_features=plFC, out_layer="pl_Lay", where_clause=waar)
                arcpy.CopyFeatures_management(in_features="pl_Lay", out_feature_class=uitFCl)
                ## 4 simpele XZ as uittekenen met schaalverdeling.
                # kolom toevoegen met de te labelen waarden
                arcpy.AddField_management(Lnm, "Tekst_XYas", "TEXT", "", "", "25")
                desc = arcpy.Describe(Lnm)
                Xmin = int(desc.extent.XMin)
                Xmax = int(desc.extent.XMax)
                Ymin = desc.extent.YMin
                Ymax = desc.extent.YMax
                Yb   = int(Ymin - 2)
                Yt   = int(Ymax + 2)
                # teken uit
                arcpy.AddMessage("XY-as uittekenen...")
                with arcpy.da.InsertCursor(Lnm, ["SHAPE@","Tekst_XYas"]) as Icursor:
                    #Y-as
                    polyline = arcpy.Polyline(arcpy.Array([arcpy.Point(Xmin, Yb), arcpy.Point(Xmin, Yt)]))
                    Icursor.insertRow([polyline,"-999"])
                    #X-as
                    polyline = arcpy.Polyline(arcpy.Array([arcpy.Point(Xmin, Yb), arcpy.Point(Xmax, Yb)]))
                    Icursor.insertRow([polyline,"-999"])
                    # stap lijntjes Y-as
                    for stap in range(Yb, Yt + 1, 1):
                        polyline = arcpy.Polyline(arcpy.Array([arcpy.Point(Xmin - 0.5, stap), arcpy.Point(Xmin, stap)]))
                        Icursor.insertRow([polyline,str(stap)])
                    # stap lijntjes X-as
                    for stap in range(Xmin, Xmax, 5):
                        polyline = arcpy.Polyline(arcpy.Array([arcpy.Point(stap, Yb - 0.5), arcpy.Point(stap, Yb)]))
                        Icursor.insertRow([polyline,str(stap)])
                    # 0 lijn is BKL ook even tekenen.
                    polyline = arcpy.Polyline(arcpy.Array([arcpy.Point(0, Yb), arcpy.Point(0, Yt)]))
                    Icursor.insertRow([polyline,"-999"])                    
                    # afsluitende vert. lijn
                    polyline = arcpy.Polyline(arcpy.Array([arcpy.Point(Xmax, Yb), arcpy.Point(Xmax, Yt)]))
                    Icursor.insertRow([polyline,"-999"])
                del Icursor
                #----------------------------------------------------------
            elif (vraag == "No"):
                arcpy.AddMessage("bestaande " + PPnm + " gebruiken")
            else:
                arcpy.AddMessage("??")
            # toevoegen aan TOC
            arcpy.AddMessage("Profiel toevoegen aan TOC...")
            MXD = arcpy.mapping.MapDocument("CURRENT")
            DF = arcpy.mapping.ListDataFrames(MXD)[0]            
            grplyr = arcpy.mapping.Layer(GRPlay)
            grplyr.name = VAK
            grplyr.visible = False
            if arcpy.Exists(VAK):
                arcpy.AddWarning("bestaande grouplayer verwijderen!")
                arcpy.Delete_management(VAK)
            arcpy.mapping.AddLayer(DF, grplyr, "TOP")
            #--
            lyr1 = arcpy.mapping.Layer(lay1)
            lyr1.replaceDataSource(workspace,"FILEGDB_WORKSPACE",PPnm)
            grplyr = arcpy.mapping.ListLayers(MXD, VAK, DF)[0]
            arcpy.mapping.AddLayerToGroup(DF,grplyr,lyr1,"BOTTOM")
            #--
            lyr2 = arcpy.mapping.Layer(lay2)
            lyr2.replaceDataSource(workspace,"FILEGDB_WORKSPACE",Pnm)
            grplyr = arcpy.mapping.ListLayers(MXD, VAK, DF)[0]
            arcpy.mapping.AddLayerToGroup(DF,grplyr,lyr2,"BOTTOM")
            #--
            lyr3 = arcpy.mapping.Layer(lay3)
            lyr3.replaceDataSource(workspace,"FILEGDB_WORKSPACE",Pnm)
            lyr3.symbology.addAllValues()
            grplyr = arcpy.mapping.ListLayers(MXD, VAK, DF)[0]
            arcpy.mapping.AddLayerToGroup(DF,grplyr,lyr3,"BOTTOM")
            #--
            lyr4 = arcpy.mapping.Layer(lay4)
            lyr4.replaceDataSource(workspace,"FILEGDB_WORKSPACE",Lnm)
            lyr4.symbology.addAllValues()
            grplyr = arcpy.mapping.ListLayers(MXD, VAK, DF)[0]
            arcpy.mapping.AddLayerToGroup(DF,grplyr,lyr4,"BOTTOM")
            #----------------------------------------------------------
            arcpy.RefreshActiveView()
            arcpy.RefreshTOC()
        else:
            arcpy.AddWarning("- er liggen geen profielen op het betreffende vak!")
        #----------------------------------------------------------
        # Als laatste dichtsbijzijnde HRD locatie opzoeken tov middelpunt van het vak.
        # XY middelpunt vak bepalen.
        arcpy.AddMessage("--------------------------\nDichtsbijzijnde HRD opzoeken...")
        feat = row[4]
        x = feat.positionAlongLine(0.5,True).firstPoint.X
        y = feat.positionAlongLine(0.5,True).firstPoint.Y
        midP = arcpy.PointGeometry(arcpy.Point(x,y),spatial_ref)
        # Nu een near met dit punt tov de HRD locaties
        naam = ''
        afst = 100000
        for hr in HRDpntLijst:
            dist = midP.distanceTo(hr[1])
            if (dist < afst):
                afst = dist
                naam = hr[2]
        arcpy.AddMessage("HRD: "+naam+"  afstand: "+str(round(afst,2))+"m")
        row[5] = naam
        #----------------------------------------------------------
        # Nu statistics opzoeken in array en toevoegen aan het vak.
        arcpy.AddMessage("\nStatistieken van het vak bepalen...")
        for st in StatsLijst:
            if st[0] == row[2]:
                arcpy.AddMessage("Statistics:  ID="+str(st[0])+" minZ="+str(st[1])+" maxZ="+str(st[2])+" dtZ="+str(st[3]))                
                row[7] = st[1]  # min Z max
                row[8] = st[2]  # mean Z max
                row[9] = st[3]  # mean DT Zspot
        #----------------------------------------------------------
        # Nu de mediaan van de normaal bepalen ipv mean.
        # met cursor lijst maken van alle normalen van het vak.
        arcpy.AddMessage("\nMediaan van de Normaal bepalen...")
        NormaalLijst = []
        with arcpy.da.SearchCursor("xxProfPnt0", [VAKkol,Pkol,"DijkNormaal"], where_clause=were) as Ncursor:
            for Nrow in Ncursor:
                NormaalLijst.append(Nrow[2])
        #arcpy.AddMessage("NormaalLijst: "+str(NormaalLijst))
        NormaalLijst.sort()
        nN = len(NormaalLijst)
        #arcpy.AddMessage("NormaalLijst lengte: "+str(len(NormaalLijst)))
        # NormaalLijst sorteren en middelste selecteren
        deNORMAAL = 0  # even leeg maken.
        mid = int(round((nN / 2),0)) - 1
        deNORMAAL = NormaalLijst[mid]
        arcpy.AddMessage("Mediaan: "+str(round(deNORMAAL,0)))
        row[6] = round(deNORMAAL,0)
        #----------------------------------------------------------
        teller += 1
        arcpy.SetProgressorPosition(teller)
        # het vak updaten.
        cursor.updateRow(row)
del row, cursor
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------
# De vakindeling die gebruikt is naar dataset kopieren.
desc = arcpy.Describe(VakFC)
Ivakken = desc.catalogPath
arcpy.CopyFeatures_management(in_features=Ivakken, out_feature_class=oDS+"/Vakken_prfl")
#---------------------------------------------------------
# tijdelijke bestanden verwijderen.
for bestand in ["xxProfPnt0","xxProfPnt","xxProfPnt_Statistics","pp_Lay","pl_Lay"]:
    arcpy.Delete_management(bestand)
#---------------------------------------------------------
arcpy.AddMessage("\n  >>>  KLAAR!  <<<")
arcpy.AddMessage("\n  >>>  Klik nu de PRFL punten in het profiel...  <<<\n")
arcpy.ResetProgressor()
