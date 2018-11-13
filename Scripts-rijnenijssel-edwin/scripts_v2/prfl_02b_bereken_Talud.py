# --------------------------------------------------------------------------
# taludprofielen helling bepalen obv zelf ingeklikte punten en aan vak koppelen.
# Witteveen+Bos
# ing. H.E.J. Nieuwland - december 2017
# --------------------------------------------------------------------------
# versie 1.0.1
# --------------------------------------------------------------------------
# 20180711 toevoegen van de 2 kolommen eruit gehaald en naar stap 1 aanmaken vakkenbestand gehaald.
# --------------------------------------------------------------------------
import string, os, sys, locale, arcpy
from time import strftime  
tijd = strftime("%m-%d-%Y %H:%M:%S")

# INPUT
VakFC       = sys.argv[1]       # Vakken FC
IDkol       = "ID"              # Kolom met id vak Dit is de unieke koppeling tussen vak en prfl file. ID in beide moet gelijk zijn.
DS          = "TALUD_DATA"
TALID       = "TALUDID"         # de gebruikte ID voor de TALUD bepaling ook aan de vakken koppelen zodat later te zien is welke vakken bij het 1e grote vak horen.
Buikol      = "CONTROLE_Buitentalud"
Binkol      = "CONTROLE_Binnentalud"
Tkol        = "TALUDpunten"     # Kolom waar het type punt in staat
#---
arcpy.env.overwriteOutput = True
arcpy.AddMessage("  >>> ----------------------------------")
arcpy.AddWarning("  >>> Berekenen hellingen per vak ")
arcpy.AddMessage("  >>> ----------------------------------\n")
#---------------------------------------------------------
#---------------------------------------------------------
# ----  START ----
#---------------------------------------------------------
# databasedir bepalen
workspace = os.path.dirname(VakFC)
if [any(ext) for ext in ('.gdb', '.mdb', '.sde') if ext in os.path.splitext(workspace)]:
    workspace = workspace
else:
    workspace = os.path.dirname(workspace)
arcpy.env.workspace = workspace

# Feature Dataset selecteren voor de FC's per vak
oDS = workspace+"/"+DS
arcpy.AddMessage("Dataset:  "+oDS)
#---------------------------------------------------------
kolommen = [IDkol, Buikol, Binkol]
# -------------------------
with arcpy.da.UpdateCursor(VakFC, kolommen) as cursor:
    for row in cursor:
        arcpy.AddMessage("\nVakID: "+str(row[0]))
        PvakNaam = "Pvak_Talud_"+str(row[0])
        arcpy.AddMessage("PvakNaam: "+str(PvakNaam))
        # Nu punten FC selecteren
        # eerst controleren of FC bestaat dan openen en de 4 punten uitlezen. oDS+"/"+
        if arcpy.Exists(PvakNaam):
            arcpy.AddMessage(" Controleren of taludpunten bestaan...")
            were = Tkol+" LIKE 'Controle_%'"
            count = len(list(i for i in arcpy.da.SearchCursor(PvakNaam, Tkol, where_clause=were)))
            arcpy.AddMessage("Aantal TALUD punten: "+str(count))
            if count == 4:                
                   
                # Door de punten loopen.
                nn = 0
                with arcpy.da.SearchCursor(PvakNaam, ["SHAPE@X", "SHAPE@Y", Tkol], where_clause=were) as cursor2:
                    for row2 in cursor2:
                        nn = nn + 1
                        arcpy.AddMessage("X: "+str(row2[0]))
                        arcpy.AddMessage("Z: "+str(row2[1]))
                        arcpy.AddMessage("Naam: "+str(row2[2]))
                        naam = str(row2[2])
                        if (naam == "Controle_Buitenteen"):
                            Xbut = row2[0]
                            Zbut = row2[1]                            
                        elif (naam == "Controle_Buitenkruin"):
                            Xbuk = row2[0]
                            Zbuk = row2[1]
                        elif (naam == "Controle_Binnenkruin"):
                            Xbik = row2[0]
                            Zbik = row2[1]
                        elif (naam == "Controle_Binnenteen"):
                            Xbit = row2[0]
                            Zbit = row2[1]                            
                        else:
                            arcpy.AddWarning("onbekend punt!")
                    # Helling berekenen
                    # Buitentalud:
                    dtX = abs(float(Xbut) - float(Xbuk))
                    dtZ = abs(float(Zbut) - float(Zbuk))
                    Hbui = dtX / dtZ
                    arcpy.AddMessage("Hbui: "+str(round(Hbui,2)))
                    # Binnentalud:
                    dtX = abs(float(Xbit) - float(Xbik))
                    dtZ = abs(float(Zbit) - float(Zbik))
                    Hbin = dtX / dtZ
                    arcpy.AddMessage("Hbin: "+str(round(Hbin,2)))
                    # berekende taludhellingen van de geklikte talud punten wegschrijven
                    row[1] = round(Hbui,2)
                    row[2] = round(Hbin,2)
                #---------------------------------------------------------
            else:
                arcpy.AddWarning("- er zijn nog geen TALUD punten ingetekend voor het betreffende vak!")
            cursor.updateRow(row)
        else:
            arcpy.AddWarning("- FC: "+PvakNaam+" bestaat niet!")
            
#---------------------------------------------------------
arcpy.AddMessage("\n  >>>  KLAAR!  <<<")
