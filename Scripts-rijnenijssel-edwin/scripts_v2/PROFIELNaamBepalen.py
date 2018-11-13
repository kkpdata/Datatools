# --------------------------------------------------------------------------
# Witteveen+Bos
# ing. H.E.J. Nieuwland - februari 2018
# --------------------------------------------------------------------------
# versie 1.0.0
# --------------------------------------------------------------------------
# PROFIELnaam bepalen obv 10m profielpunt op de referentielijn
# --------------------------------------------------------------------------
import arcpy, sys, os
arcpy.env.overwriteOutput = True
# User input
inLine = sys.argv[1]       # in 10m profielpunten
VAKkol = "PROFIELNAAM"     # PROFIELnaam
inRT   = sys.argv[2]       # in routesysteem
Rkol   = "ROUTE_ID"        # de route kolom opbouw: 47_144
traj   = sys.argv[3]       # Normtrajectnummer
kol1   = "AFSTAND_TOT_DIJKPAAL"
kol2   = "RFTOMSCH"
#-------------------------------------------------------
arcpy.AddMessage("\n  >>> START PROFIELNAAM BEPALEN... <<<")
# describe de geometry
lineDesc = arcpy.Describe(inLine)
shapefieldname = lineDesc.ShapeFieldName
# cursor
lines = arcpy.UpdateCursor(inLine)
for line in lines:
    # lijn uitlezen en begin en eindpunt selecteren.
    lineGeom = line.getValue(shapefieldname)
    endPoints = lineGeom  #, lineGeom.lastPoint
    arcpy.AddMessage("\n  Punt: "+str(line.OBJECTID))
    uitPNT = arcpy.CreateFeatureclass_management("in_memory", "BeginEindPNT", "POINT", "", "", "", inLine)
    ptRows = arcpy.InsertCursor(uitPNT)
    ptRow = ptRows.newRow()
    ptRow.shape = endPoints
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
        dijkpl = naam.split("_")[1]
        afst = r.MEASPnt
        VanTot.append([int(dijkpl),int(afst)])
    del Mtabel
    VanTot = sorted(VanTot)
    nm = str(traj)+"_dp"+str(VanTot[0][0])+"+"+str(VanTot[0][1])
    arcpy.AddMessage("  PROFIELnaam: "+nm)
    line.setValue(VAKkol,nm)
    line.setValue(kol1,str(VanTot[0][1]))
    line.setValue(kol2,str(VanTot[0][0]))
    lines.updateRow(line)
arcpy.AddMessage("\n  >>> KLAAR! <<<")
