# --------------------------------------------------------------------------
# Witteveen+Bos
# ing. H.E.J. Nieuwland - maart 2018
# --------------------------------------------------------------------------
# versie 1.0.0
# --------------------------------------------------------------------------
# kolom PROFIELNAAM opsplitsen in dp en dp_afst
# --------------------------------------------------------------------------
import arcpy, sys

arcpy.env.overwriteOutput = True
#---------------------------------------------------------
# INPUT
DeLyr      = sys.argv[1]    # de layer
kol1       = sys.argv[2]    # kolom PROFIELNAAM
zoekstr    = sys.argv[3]    # specifieke zoekstring dijkring 48-1
okol       = "dp"           # uitvoer kolom met dijkpaal
okol2      = "dp_afst"      # uitvoer kolom met afstand
#---------------------------------------------------------
# ----  START
arcpy.AddMessage("\n>>  START  <<")
try:
    arcpy.AddField_management(DeLyr, okol, "SHORT", "4")
    arcpy.AddMessage("Aanmaken kolom "+okol+"...")
except:
    arcpy.AddWarning("Kolom ("+str(okol)+") bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddField_management(DeLyr, okol2, "SHORT", "4")
    arcpy.AddMessage("Aanmaken kolom "+okol2+"...")
except:
    arcpy.AddWarning("Kolom ("+str(okol2)+") bestaat al! Controleer zelf of type en length juist zijn.")
arcpy.AddMessage("Splitsen kolom "+kol1+"...")
# dijkpaal selecteren
expr1 = "!"+kol1+"!.replace('"+zoekstr+"','').split('+')[0]"
arcpy.CalculateField_management(in_table=DeLyr, field=okol, expression=expr1, expression_type="PYTHON_9.3")
# afstand selecteren
expr2 = "!"+kol1+"!.replace('"+zoekstr+"','').split('+')[1]"
arcpy.CalculateField_management(in_table=DeLyr, field=okol2, expression=expr2, expression_type="PYTHON_9.3")
arcpy.AddMessage(">> Klaar <<")
