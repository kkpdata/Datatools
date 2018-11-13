# --------------------------------------------------------------------------
# Witteveen+Bos
# ing. H.E.J. Nieuwland - maart 2018
# --------------------------------------------------------------------------
# versie 1.0.0
# --------------------------------------------------------------------------
# sorteren op 2 kolommen en uniek nr toevoegen aan nieuwe kolom
# --------------------------------------------------------------------------
import arcpy, sys
arcpy.env.overwriteOutput = True
#---------------------------------------------------------
# INPUT
DeLyr      = sys.argv[1]      # de layer
kol1       = sys.argv[2]      # sorteerkolom 1
kol2       = sys.argv[3]      # sorteerkolom 2
okol       = sys.argv[4]      # uitvoer kolom
okol2      = sys.argv[5]      # uitvoer kolom met 5 en 10 punten
#---------------------------------------------------------
# ----  START
arcpy.AddMessage("\n>>  START  <<")
try:
    arcpy.AddField_management(DeLyr, okol, "LONG", "8")
    arcpy.AddMessage("Aanmaken kolom "+okol+"...")
except:
    arcpy.AddWarning("Kolom ("+str(okol)+") bestaat al! Controleer zelf of type en length juist zijn.")
try:
    arcpy.AddField_management(DeLyr, okol2, "LONG", "3")
    arcpy.AddMessage("Aanmaken kolom "+okol2+"...")
except:
    arcpy.AddWarning("Kolom ("+str(okol2)+") bestaat al! Controleer zelf of type en length juist zijn.")
nr = 0
kols = []
kols.append(kol1)
kols.append(kol2)
kols.append(okol)
kols.append(okol2)
sql_Klaus = "ORDER BY "+kol1+", "+kol2

arcpy.AddMessage("Bestand sorteren op "+kol1+" en "+kol2+" ...")

with arcpy.da.UpdateCursor(DeLyr, kols, sql_clause=(None, sql_Klaus)) as cursor:    
    for row in cursor:
        nr = nr + 1
        #arcpy.AddMessage(str(nr))
        row[2] = nr
        if nr%5==0:            
            if nr%10==0:
                #arcpy.AddMessage(str(nr)+'is multiple of 5 en 10')
                row[3] = 100
            else:
                #arcpy.AddMessage(str(nr)+'is multiple of 5')
                row[3] = 50
        cursor.updateRow(row)
del row, cursor
arcpy.AddMessage(">> Klaar <<")
