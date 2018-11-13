# --------------------------------------------------------------------------
# Witteveen+Bos
# ing. H.E.J. Nieuwland - februari 2018
# --------------------------------------------------------------------------
# versie 1.0.1
# --------------------------------------------------------------------------
# Vaknaam bepalen obv begin en eindpunt vak mbv route van referentielijn
# zfill toegevoegd om de dijkpaal en afstand in de naam uit te vullen tot 3 karakters
# --------------------------------------------------------------------------
import arcpy, sys, os
arcpy.env.overwriteOutput = True
# User input
inLine = sys.argv[1]       # in vakindeling
VAKkol = "Vaknaam"         # vaknaam
inRT   = sys.argv[2]       # in routesysteem
Rkol   = "ROUTE_ID"        # de route kolom opbouw: 47_144
traj   = sys.argv[3]       # Normtrajectnummer
#spoor  = sys.argv[4]       # Beoordelingsspoor
#-------------------------------------------------------
arcpy.AddMessage("\n  >>> START VAKNAAM BEPALEN... <<<")
# describe de geometry
lineDesc = arcpy.Describe(inLine)
shapefieldname = lineDesc.ShapeFieldName
# cursor
lines = arcpy.UpdateCursor(inLine)
for line in lines:
    # lijn uitlezen en begin en eindpunt selecteren.
    lineGeom = line.getValue(shapefieldname)
    endPoints = lineGeom.firstPoint, lineGeom.lastPoint
    arcpy.AddMessage("\n  Lijnstuk: "+str(line.OBJECTID))
    uitPNT = arcpy.CreateFeatureclass_management("in_memory", "BeginEindPNT", "POINT", "", "", "", inLine)
    ptRows = arcpy.InsertCursor(uitPNT)
    for pt in endPoints:
        ptRow = ptRows.newRow()
        ptRow.shape = pt
        ptRows.insertRow(ptRow)
    # Nu locatie op route zoeken
    tol = "5 Meters"            # Zoekafstand 5 meter
    tbl = "locate_points"
    props = "RID POINT MEASPnt"  # uitvoer kolommen
    # Execute LocateFeaturesAlongRoutes
    Mtabel = arcpy.LocateFeaturesAlongRoutes_lr(uitPNT, inRT, Rkol, tol, tbl, props)
    meas = arcpy.SearchCursor(Mtabel)
    VanTot = []
    for r in meas:
        naam = r.RID
        #traject = naam.split("_")[0]
        dijkpl = naam.split("_")[1]
        afst = r.MEASPnt
        VanTot.append([int(dijkpl),int(afst)])
    del Mtabel
    VanTot = sorted(VanTot)
    #nm1 = str(traj)+"_"+spoor+"_dp"
    nm1 = str(traj)+"_dp"
    # als de afstand tot de dijkpaal > 0 is dan verwerken
    if VanTot[0][1] > 0:
        nm2 = str(VanTot[0][0]).zfill(3)+"+"+str(VanTot[0][1]).zfill(3)
    else:
        nm2 = str(VanTot[0][0]).zfill(3)+"+000"
    if VanTot[1][1] > 0:
        nm3 = str(VanTot[1][0]).zfill(3)+"+"+str(VanTot[1][1]).zfill(3)
    else:
        nm3 = str(VanTot[1][0]).zfill(3)+"+000"
    nm = nm1+nm2+"-dp"+nm3
    arcpy.AddMessage("  Nieuwe vaknaam: "+nm)
    line.setValue(VAKkol,nm)
    lines.updateRow(line)
arcpy.Delete_management(tbl)
arcpy.AddMessage("\n  >>> KLAAR! <<<")
