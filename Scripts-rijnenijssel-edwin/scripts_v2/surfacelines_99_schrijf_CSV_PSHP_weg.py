# --------------------------------------------------------------------------
# Witteveen+Bos
# ing. H.E.J. Nieuwland - maart 2018
# --------------------------------------------------------------------------
# versie 1.0.0
# --------------------------------------------------------------------------
# Surfaceline als CSV exporteren
# 08-08-2018 - Er mogen meerdere representatieve profielen zijn die worden dan allemaal weggeschreven.
# --------------------------------------------------------------------------
import string, os, sys, locale, arcpy
# INPUT
VakFC        = sys.argv[1]                 # Profiellijnen FC met de vakken
odir         = sys.argv[2]                 # uitvoer map
PnmKol       = "PROFIELNAAM"               # kolom met profielnaam tbv def query
Kol          = "RepresentatiefProfiel"     # Representatief kolom
Skol         = "SORTEERVOLGORDE2"          # kolom met de sorteervolgorde van de punten.
Xkol         = "X_WAARDE"
Ykol         = "Y_WAARDE"
Zkol         = "Z_WAARDE"
BGkol        = "LENGTE_TOT_BG"             # lengte van alle punten tot het beginpunt v/h profiel
oCSV_naam    = "Surfacelines.csv"          # de naam van de uitvoer csv
# databasedir bepalen
workspace = os.path.dirname(arcpy.Describe(VakFC).catalogPath)
arcpy.env.workspace = workspace
#---
arcpy.env.overwriteOutput = True
arcpy.AddMessage("\n  >>> ----------------------------------")
arcpy.AddMessage("  >>> Wegschrijven surfaceline ")
arcpy.AddMessage("  >>> ----------------------------------")
#---------------------------------------------------------
#---------------------------------------------------------
# -------  START -------
#---------------------------------------------------------
FOUT = False   # als de benodigde variabelen niet juist zijn dan geen Surfaceline wegschrijven!
#-- De dwarsprofiel FC
lFC = arcpy.Describe(VakFC).baseName
plFC = lFC.replace("SRFVAK_L_","SRFVAK_P_")
arcpy.AddMessage("Profiellijn:      "+lFC)
arcpy.AddMessage("Profiellijn Punt: "+plFC+"\n")
#---------------------------------------------------------
# Als de FC er niet is dan vak overslaan.
Lchk = arcpy.Exists(lFC)
plchk = arcpy.Exists(plFC)
#---------------------------------------------------------
were = Kol + " = 'Representatief profiel'"
# Eerst Surfaceline wegschrijven
kolommen = ["OID@", "SHAPE@", PnmKol, Kol]
Pnaam = ""
if Lchk and FOUT == False:
    # uitlezen.
    try:
        count = len(list(i for i in arcpy.da.SearchCursor(lFC, kolommen, where_clause=were)))
        arcpy.AddMessage("Aantal dwarsprofielen: "+str(count))
    except:
        arcpy.AddWarning("  Nog geen representatief profiel gekozen!")
        FOUT = True
    if count == 0:
        arcpy.AddError("  is 0!!")
        FOUT = True
    else:
        arcpy.AddMessage("  is ok")
    # Doorgaan als er een profiel is.
    if not FOUT:
        XYlijst  = []
        VOORLlst = []
        TALUDlst = []
        # -------------------------
        # Van het dwarsprofiel lijntje hebben we niet meer de RD XYZ
        # Dus hier naam van het profiel uit halen en de dwarsprofielpunten seleteren
        with arcpy.da.SearchCursor(lFC, kolommen, where_clause=were) as cursor:
            for row in cursor:
                Pnaam = row[2]
                arcpy.AddMessage("\nProfiel: "+Pnaam+"\n")
                # Nu naar de punten
                were = PnmKol + " = '"+Pnaam+"'"
                XYZlijst = Pnaam
                Pkolommen = [Xkol, Ykol, Zkol, PnmKol, Skol, BGkol]
                with arcpy.da.SearchCursor(plFC, Pkolommen, where_clause=were) as cursor2:
                    for row2 in cursor2:
                        X = round(row2[0],4)
                        Y = round(row2[1],4)
                        Z = round(row2[2],3)
                        #arcpy.AddMessage("XYZ: "+str(X)+"/"+str(Y)+"/"+str(Z))
                        XYZlijst = XYZlijst+";"+str(X)+";"+str(Y)+";"+str(Z)
                    # Open csv file
                    arcpy.AddMessage("Wegschrijven naar: "+ oCSV_naam+" ...")
                    if arcpy.Exists(odir+"/"+oCSV_naam):
                        arcpy.AddMessage("Profiel wordt toegevoegd aan uitvoer CSV!")
                        ll = open(odir+"/"+oCSV_naam, "a")
                    else:
                        arcpy.AddMessage("Aanmaken uitvoer CSV...")
                        ll = open(odir+"/"+oCSV_naam, "w")
                        ll.write("LOCATIONID;X1;Y1;Z1;.....;Xn;Yn;Zn;(Profiel)\n")
                    # Profiel wegschrijven.
                    ll.write(XYZlijst+"\n")
                    #-------------------------------------------------------------------------------
                    # Open csv file 2 per profiel X_RD;Y_RD;Afstand;Z wegschrijven in een losse file
                    oCSV2_naam = Pnaam+".csv"
                    arcpy.AddMessage("Profiel los wegschrijven naar: "+ oCSV2_naam+" ...")
                    if arcpy.Exists(odir+"/"+oCSV2_naam):
                        arcpy.AddMessage("Profiel CSV bestaat al en wordt overschreven!")
                        ll2 = open(odir+"/"+oCSV2_naam, "w")
                    else:
                        arcpy.AddMessage("Profiel CSV aanmaken...")
                        ll2 = open(odir+"/"+oCSV2_naam, "w")
                    # Profiel wegschrijven
                    del row2
                    cursor2.reset()
                    ll2.write("X-RD;Y_RD;Afstand;Z\n")
                    for row3 in cursor2:
                        X = round(row3[0],4)
                        Y = round(row3[1],4)
                        Z = round(row3[2],3)
                        afst = round(row3[5],2)
                        #arcpy.AddMessage("XYZ: "+str(X)+"/"+str(Y)+"/"+str(Z)+"/"+str(afst))
                        XYafstZ = str(X)+";"+str(Y)+";"+str(afst)+";"+str(Z)
                        ll2.write(XYafstZ+"\n")
                del row3, cursor2
#-----------------------------------------------------------------------------------------------
arcpy.AddMessage("\n  >>>  KLAAR!  <<<")
