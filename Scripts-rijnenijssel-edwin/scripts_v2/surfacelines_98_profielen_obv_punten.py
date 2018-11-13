# --------------------------------------------------------------------------
# Wegschrijven profielen per vak tbv surfaceline tbv Ringtoets
# Witteveen+Bos
# ing. H.E.J. Nieuwland - januari 2018
# --------------------------------------------------------------------------
# versie 1.0.1
# --------------------------------------------------------------------------
# mrt 2018 Vaknaam ook uitlezen (VAK) en als naam van de groeplayer toepassen.
# mrt 2018 Deze kopie gemaakt om nu zonder vakken alleen obv een selectie 10m punten een profiel te maken
# --------------------------------------------------------------------------
import string, os, sys, locale, arcpy, pythonaddins, time, datetime 

# INPUT
P10FC       = sys.argv[1]    # PWK punten op de lijn FC
ID          = "Ps_"          # uniek ID voor dit punten 
VAK         = "Psel_"        # Kolom met vaknaam voor de naam van de grouplayer
Pkol        = "PROFIELNAAM"  # Naam van het profiel uit FME
ppFC        = sys.argv[2]    # profielpunten FC
plFC        = sys.argv[3]    # profiellijnen FC
GRPlay      = os.path.dirname(__file__)+"/GroupVAK.lyr" # lege group layer voor de profielen.
lay2        = os.path.dirname(__file__)+"/Slijn_KenmerkendePunten.lyr"
lay4        = os.path.dirname(__file__)+"/Proflijnen.lyr"
Conkol      = "GebruikVoorDWP"   # in deze kolom kan men aangeven of het profiel wel(1) of niet(9) moet worden meegenomen
#---
# Datum tijd naar een uniek nummer
ses = int(time.mktime(datetime.datetime.today().timetuple()))
ID = ID+str(ses)
VAK = VAK+str(ses)
arcpy.AddMessage(ID)
#--
arcpy.env.overwriteOutput = True
arcpy.AddMessage("  >>> ----------------------------------")
arcpy.AddWarning("  >>> Wegschrijven profielen van de selectie ")
arcpy.AddMessage("  >>> ----------------------------------\n")
#---------------------------------------------------------
#---------------------------------------------------------
# ----  START ----
#---------------------------------------------------------
arcpy.AddMessage("Profielpunten: \n"+ppFC)
# databasedir bepalen
workspace = os.path.dirname(ppFC)

if [any(ext) for ext in ('.gdb', '.mdb', '.sde') if ext in os.path.splitext(workspace)]:
    workspace = workspace
else:
    workspace = os.path.dirname(workspace)
arcpy.env.workspace = workspace
# Feature Dataset aanmaken voor de FC's per vak
oDS = workspace+"/SRFLINE_SDATA"
arcpy.AddMessage("Uitvoer Dataset:  "+oDS+"\n")
if not arcpy.Exists(oDS):
    arcpy.CreateFeatureDataset_management(workspace, "SRFLINE_SDATA")
    arcpy.AddMessage("Uitvoer Dataset:  SRFLINE_SDATA aangemaakt!")
else:
    arcpy.AddMessage("Bestaande uitvoer Dataset:  SRFLINE_SDATA gebruiken!")
#---------------------------------------------------------
# Om de mogelijkheid te hebben om na het genereren van de dwarsprofielen per vak verkeerder profielen uit te kunnen
# zetten wordt er een kolom aan het basis profiellijnen en punten bestand(PWK_DWARSPROFIEL_POINT en PWK_DWARSPROFIEL_LINE)
# toegevoegd incl een domein met ja/nee
try:
    arcpy.AddMessage("Domein aanmaken: ")
    arcpy.CreateDomain_management(workspace, 'Meenemen', 'Meenemen', "TEXT", "CODED")
    arcpy.AddCodedValueToDomain_management(workspace, 'Meenemen', 'ja', 'ja')
    arcpy.AddCodedValueToDomain_management(workspace, 'Meenemen', 'nee', 'nee')
except:
    arcpy.AddWarning("Domein al toegevoegd!")
# Kolom toevoegen incl. domein
try:
    arcpy.AddField_management(ppFC, "meenemen", "TEXT", "", "", 3, "", "NULLABLE", "NON_REQUIRED", "Meenemen")
    #arcpy.AssignDefaultToField_management(in_table=ppFC, field_name="meenemen", default_value="ja", subtype_code="", clear_value="false")
    arcpy.AddField_management(plFC, "meenemen", "TEXT", "", "", 3, "", "NULLABLE", "NON_REQUIRED", "Meenemen")
    #arcpy.AssignDefaultToField_management(in_table=plFC, field_name="meenemen", default_value="ja", subtype_code="", clear_value="false")
    # ff alles op ja zetten
    arcpy.CalculateField_management(in_table=ppFC, field="meenemen", expression='"ja"', expression_type="PYTHON_9.3")
    arcpy.CalculateField_management(in_table=plFC, field="meenemen", expression='"ja"', expression_type="PYTHON_9.3")
except:
    arcpy.AddWarning("Kolom al toegevoegd!")
#---------------------------------------------------------    
# Eerst kijken of er wel een selectie is min=1
n = len(list(i for i in arcpy.da.SearchCursor(P10FC,"OID@")))
arcpy.AddMessage("Er is/zijn: "+str(n)+" profielpunt(en) geselecteerd!")
# controle op n selected
if n == 0:
    arcpy.AddError("Selecteer minimaal 1 profielpunt!")
    sys.exit()
if n >= 1:
    #--- Nu punten verwerken
    # Eerst alleen de punten selecteren die we mee willen nemen.
    arcpy.Select_analysis(in_features=P10FC, out_feature_class="xxProfPnt0", where_clause=Conkol+" = 1")
    #---------------------------------------------------------
    # Niet alle profielen meenemen. Zie kolom GebruikVoorDWP als deze niet 1 is dan ook niet meenemen.
    arcpy.Select_analysis(in_features="xxProfPnt0", out_feature_class="xxProfPnt", where_clause=Conkol+" = 1")
    #---------------------------------------------------------
    # Door de punten loopen en PROFIELNAAM in lijst zetten.
    profs = []
    waar = ""
    nn = 0
    with arcpy.da.SearchCursor("xxProfPnt", [Pkol]) as cursor2:
        for row2 in cursor2:
            nn = nn + 1
            profs.append(row2[0])
            if nn == 1:
                waar = Pkol+" IN ( '"+row2[0]+"'"
            else:
                waar = waar+",'"+row2[0]+"'"
        waar = waar + ")"
    #---------------------------------------------------------
    # Alleen als er profielnamen zijn geselecteerd dan verder.
    if waar <> "":
        # 3 alle profielen selecteren en wegschrijven.
        Pnm = "SRFVAK_P_"+ID
        uitFCp = oDS+"/"+Pnm
        Lnm = "SRFVAK_L_"+ID
        uitFCl = oDS+"/"+Lnm
        # Als de profiel bestanden al bestaan eerst vragen of ze overschreven moeten worden.
        vraag = "Geen"
        if arcpy.Exists(uitFCp)or arcpy.Exists(uitFCl):
            vraag = pythonaddins.MessageBox("Voor dit vak bestaan al profiel bestanden! Wil je deze verwijderen?", "Bestaat al", 4)
        #--
        if (vraag == "Yes") or (vraag == "Geen"):
            if (vraag == "Yes"):
                arcpy.AddWarning("verwijderen! xxx")
                arcpy.Delete_management(uitFCp)
                arcpy.Delete_management(uitFCl)
            # FC aanmaken
            arcpy.AddMessage(uitFCp + " aanmaken")
            waar2 = waar+" AND (OPMERKING IS NULL OR OPMERKING <> 'BKL_MAX_Z_AHN') AND Z_WAARDE > -10"   # niet de zelf toegevoegde max Z BKL punten gebruiken!
            #arcpy.AddMessage(waar2)
            arcpy.MakeFeatureLayer_management(in_features=ppFC, out_layer="pp_Lay", where_clause=waar2)
            arcpy.CopyFeatures_management(in_features="pp_Lay", out_feature_class=uitFCp)
            # Lijnen            
            arcpy.AddMessage(uitFCl + " aanmaken")
            #arcpy.AddMessage(waar)                
            arcpy.MakeFeatureLayer_management(in_features=plFC, out_layer="pl_Lay", where_clause=waar)
            arcpy.CopyFeatures_management(in_features="pl_Lay", out_feature_class=uitFCl)
            arcpy.AddField_management(Lnm, "RepresentatiefProfiel", "TEXT", "", "", "50")
        elif (vraag == "No"):
            arcpy.AddMessage("bestaande " + Lnm + " gebruiken")
        else:
            arcpy.AddMessage("??")
        # toevoegen aan TOC
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
        lyr2 = arcpy.mapping.Layer(lay2)
        lyr2.replaceDataSource(workspace,"FILEGDB_WORKSPACE",Pnm)
        grplyr = arcpy.mapping.ListLayers(MXD, VAK, DF)[0]
        arcpy.mapping.AddLayerToGroup(DF,grplyr,lyr2,"BOTTOM")
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
        #----------------------------------------------------------
        lyr4 = arcpy.mapping.Layer(lay4)
        lyr4.replaceDataSource(workspace,"FILEGDB_WORKSPACE",Lnm)
        lyr4.symbology.addAllValues()
        grplyr = arcpy.mapping.ListLayers(MXD, VAK, DF)[0]
        arcpy.mapping.AddLayerToGroup(DF,grplyr,lyr4,"BOTTOM")
        #--
        arcpy.RefreshActiveView()
        arcpy.RefreshTOC()
    else:
        arcpy.AddWarning("- er kunnen geen profielen worden uitgetekend!")
#---------------------------------------------------------
arcpy.AddMessage("\n")
#---------------------------------------------------------
# tijdelijke bestanden verwijderen.
for bestand in ["xxProfPnt0","xxProfPnt","pp_Lay","pl_Lay"]:
    arcpy.Delete_management(bestand)
#---------------------------------------------------------
arcpy.AddWarning("\n  >>>  KLAAR!  <<<")
