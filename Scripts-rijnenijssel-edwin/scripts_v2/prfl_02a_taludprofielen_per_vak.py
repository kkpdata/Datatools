# --------------------------------------------------------------------------
# Wegschrijven profielen per vak tbv Talud bepaling tbv Ringtoets
# Witteveen+Bos
# ing. H.E.J. Nieuwland - november 2017
# --------------------------------------------------------------------------
# versie 1.0.1
# --------------------------------------------------------------------------
# 20180411 niet hele dataset verwijderen maar per profiel.
# 20180411 kopie van talud vakken nu altijd vanaf de FC niet de layer.
# --------------------------------------------------------------------------
import string, os, sys, locale, arcpy, pythonaddins
from time import strftime  
#tijd = strftime("%m-%d-%Y %H:%M:%S")
tijd = strftime("%Y%m%d_%H%M%S")

# INPUT
VakFC       = sys.argv[1]    # Vakken FC
IDkol       = "ID"           # Kolom met id vak Dit is de unieke koppeling tussen vak en prfl file. ID in beide moet gelijk zijn.
P10FC       = sys.argv[2]    # PWK punten op de lijn FC
Pkol        = "PROFIELNAAM"  # Naam van het profiel uit FME
ppFC        = sys.argv[3]    # profielpunten FC
plFC        = sys.argv[4]    # profiellijnen FC
DELL        = sys.argv[5]    # Als er al profiellen zijn dan deze verwijderen. (true) anders false of #
GRPlay      = os.path.dirname(__file__)+"/GroupVAK.lyr" # lege group layers voor de profielen.
lay1        = os.path.dirname(__file__)+"/TALUD punten.lyr"
lay2        = os.path.dirname(__file__)+"/TALUD_Kenmerkende punten.lyr"
lay3        = os.path.dirname(__file__)+"/Profpunten.lyr"
lay4        = os.path.dirname(__file__)+"/Proflijnen_prfl.lyr"
Conkol      = "ControleTalud"   # in deze kolom heeft men aangeven of het profiel wel(1) of niet(9) moet worden meegenomen
DS          = "TALUD_DATA"      # naam dataset waar de profielen in komen te staan.
TALID       = "TALUDID"         # de gebruikte ID voor de TALUD bepaling ook aan de vakken koppelen zodat later te zien is welke vakken bij het 1e grote vak horen.
#---
# variabele DELL naar boolean
if DELL == 'true':
    DELL = True
else:
    DELL = False
arcpy.env.overwriteOutput = True
arcpy.AddMessage("  >>> ----------------------------------")
arcpy.AddWarning("  >>> Wegschrijven profielpunten per vak\n  >>> tbv Talud bepaling")
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
oDS = workspace+"/"+DS
if not arcpy.Exists(oDS):
    arcpy.CreateFeatureDataset_management(workspace, DS)
    arcpy.AddMessage("Uitvoer Dataset:  "+DS+" aangemaakt!")
else:
    arcpy.AddMessage("Bestaande uitvoer Dataset:  "+DS+" gebruiken!")
#---------------------------------------------------------
# Vakid overzetten naar Taludid
arcpy.CalculateField_management(VakFC, TALID, "["+IDkol+"]", "VB")
#---------------------------------------------------------
# 1 vaknaam koppelen aan dwarsprofielpunten.
# Eerst alleen de punten selecteren die we mee willen nemen. Zie kolom GebruikVoorDWP als deze niet 1 is dan ook niet meenemen.
arcpy.Select_analysis(in_features=P10FC, out_feature_class="xxTALUDPnt", where_clause=Conkol+" = 1")
# Create a new fieldmappings and add the two input feature classes.
fieldmap = arcpy.FieldMappings()
fieldmap.addTable("xxTALUDPnt")
fieldmap.addTable(VakFC)
arcpy.SpatialJoin_analysis(target_features="xxTALUDPnt", join_features=VakFC, out_feature_class="xxProfPnt", join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_ALL", field_mapping=fieldmap, match_option="CLOSEST", search_radius="5 Meters")
fieldmap.removeAll()
#---------------------------------------------------------
#---------------------------------------------------------
# 2 dan per vak naam uitlezen, profielnamen selecteren en lijst van maken.
kolommen = ["OID@", "SHAPE@LENGTH", IDkol]
# Aantal vakken uitlezen.
count = len(list(i for i in arcpy.da.SearchCursor(VakFC, kolommen)))
arcpy.AddMessage("Aantal vakken: "+str(count))
# -------------------------
with arcpy.da.SearchCursor(VakFC, kolommen) as cursor:
    for row in cursor:
        arcpy.AddMessage("\nVakID: "+str(row[2]))
        ID = row[2].replace('-','_')
        tID = "Talud_"+ ID
        # Nu profielpunten selecteren
        were = IDkol+" = '"+str(row[2])+"'"
        # Door de punten loopen en PROFIELNAAM in lijst zetten.
        profs = []
        waar = ""
        nn = 0
        with arcpy.da.SearchCursor("xxProfPnt", [Pkol], where_clause=were) as cursor2:
            for row2 in cursor2:
                nn = nn + 1
                #arcpy.AddMessage("Profiel: "+str(row2[0]))
                profs.append(row2[0])
                if nn == 1:
                    waar = Pkol+" = '"+row2[0]+"'"
                else:
                    waar = waar+" or "+Pkol+" = '"+row2[0]+"'"
        #---------------------------------------------------------
        # Alleen als er profielnamen zijn geselecteerd dan verder.
        if waar <> "":
            # 3 alle profielen selecteren en wegschrijven.
            Pnm = "Pvak_Talud_"+ID
            uitFCp = oDS+"/"+Pnm
            arcpy.AddMessage(uitFCp)
            # Lijnen
            Lnm = "Lvak_Talud_"+ID
            uitFCl = oDS+"/"+Lnm
            arcpy.AddMessage(uitFCl)
            # Controleren of de punten FC er al is. Zo ja dan vragen of deze verwijderd moet worden.
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
            if arcpy.Exists(uitFCp)or arcpy.Exists(uitFCl):
                arcpy.AddWarning("bestaat...")
                vraag = "No"
            #--            
            if DELL or (vraag == "Geen"):
                # FC aanmaken
                arcpy.AddMessage(Pnm + " aanmaken")
                arcpy.MakeFeatureLayer_management(in_features=ppFC, out_layer="pp_Lay", where_clause=waar)
                arcpy.CopyFeatures_management(in_features="pp_Lay", out_feature_class=uitFCp)
                # en de dwplijnen aanmaken
                arcpy.AddMessage(Lnm + " aanmaken")
                arcpy.MakeFeatureLayer_management(in_features=plFC, out_layer="pl_Lay", where_clause=waar)
                arcpy.CopyFeatures_management(in_features="pl_Lay", out_feature_class=uitFCl)
                #----------------------------------------------------------
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
                cursor = arcpy.da.InsertCursor(Lnm, ["SHAPE@","Tekst_XYas"])
                #Y-as
                polyline = arcpy.Polyline(arcpy.Array([arcpy.Point(Xmin, Yb), arcpy.Point(Xmin, Yt)]))
                cursor.insertRow([polyline,"-999"])
                #X-as
                polyline = arcpy.Polyline(arcpy.Array([arcpy.Point(Xmin, Yb), arcpy.Point(Xmax, Yb)]))
                cursor.insertRow([polyline,"-999"])
                # stap lijntjes Y-as
                for stap in range(Yb, Yt + 1, 1):
                    polyline = arcpy.Polyline(arcpy.Array([arcpy.Point(Xmin - 0.5, stap), arcpy.Point(Xmin, stap)]))
                    cursor.insertRow([polyline,str(stap)])
                # stap lijntjes X-as
                for stap in range(Xmin, Xmax, 5):
                    polyline = arcpy.Polyline(arcpy.Array([arcpy.Point(stap, Yb - 0.5), arcpy.Point(stap, Yb)]))
                    cursor.insertRow([polyline,str(stap)])
                # 0 lijn is BKL ook even tekenen.
                polyline = arcpy.Polyline(arcpy.Array([arcpy.Point(0, Yb), arcpy.Point(0, Yt)]))
                cursor.insertRow([polyline,"-999"])
                # afsluitende vert. lijn
                polyline = arcpy.Polyline(arcpy.Array([arcpy.Point(Xmax, Yb), arcpy.Point(Xmax, Yt)]))
                cursor.insertRow([polyline,"-999"])
            elif (vraag == "No"):
                arcpy.AddMessage("bestaande " + Pnm +" en "+Lnm+ " gebruiken")
            else:
                arcpy.AddMessage("??")
            # toevoegen aan TOC
            MXD = arcpy.mapping.MapDocument("CURRENT")
            DF = arcpy.mapping.ListDataFrames(MXD)[0]            
            grplyr = arcpy.mapping.Layer(GRPlay)
            grplyr.name = tID
            grplyr.visible = False
            # Als grouplayer bestaat dan verwijderen.
            if arcpy.Exists(tID):
                arcpy.AddWarning("bestaande grouplayer verwijderen!")
                arcpy.Delete_management(tID)
            arcpy.mapping.AddLayer(DF, grplyr, "TOP")
            #--
            lyr1 = arcpy.mapping.Layer(lay1)
            lyr1.replaceDataSource(workspace,"FILEGDB_WORKSPACE",Pnm)
            grplyr = arcpy.mapping.ListLayers(MXD, tID, DF)[0]
            arcpy.mapping.AddLayerToGroup(DF,grplyr,lyr1,"BOTTOM")
            #--
            lyr2 = arcpy.mapping.Layer(lay2)
            lyr2.replaceDataSource(workspace,"FILEGDB_WORKSPACE",Pnm)
            grplyr = arcpy.mapping.ListLayers(MXD, tID, DF)[0]
            arcpy.mapping.AddLayerToGroup(DF,grplyr,lyr2,"BOTTOM")
            #--
            lyr3 = arcpy.mapping.Layer(lay3)
            lyr3.replaceDataSource(workspace,"FILEGDB_WORKSPACE",Pnm)
            lyr3.symbology.addAllValues()
            grplyr = arcpy.mapping.ListLayers(MXD, tID, DF)[0]
            arcpy.mapping.AddLayerToGroup(DF,grplyr,lyr3,"BOTTOM")
            #--
            lyr4 = arcpy.mapping.Layer(lay4)
            lyr4.replaceDataSource(workspace,"FILEGDB_WORKSPACE",Lnm)
            lyr4.symbology.addAllValues()
            grplyr = arcpy.mapping.ListLayers(MXD, tID, DF)[0]
            arcpy.mapping.AddLayerToGroup(DF,grplyr,lyr4,"BOTTOM")
            #----------------------------------------------------------
            arcpy.RefreshActiveView()
            arcpy.RefreshTOC()
        else:
            arcpy.AddWarning("- er liggen geen profielen op het betreffende vak!")
#---------------------------------------------------------
#---------------------------------------------------------
# De vakindeling die gebruikt is naar dataset kopieren.
desc = arcpy.Describe(VakFC)
Ivakken = desc.catalogPath
arcpy.CopyFeatures_management(in_features=Ivakken, out_feature_class=oDS+"/Vakken_Taludbepaling")
#---------------------------------------------------------
# tijdelijke bestanden verwijderen.
for bestand in ["xxProfPnt0","xxProfPnt","xxTALUDPnt","pp_Lay","pl_Lay"]:
    arcpy.Delete_management(bestand)
#---------------------------------------------------------
arcpy.AddWarning("\n  >>>  KLAAR!  <<<")
arcpy.AddWarning("\n  >>>  Teken nu de 4 talud knikpunten in....  <<<\n")

