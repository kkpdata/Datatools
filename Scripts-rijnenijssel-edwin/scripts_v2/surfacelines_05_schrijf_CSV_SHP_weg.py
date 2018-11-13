# --------------------------------------------------------------------------
# Witteveen+Bos
# ing. H.E.J. Nieuwland - januari 2018
# --------------------------------------------------------------------------
# versie 1.0.3
# --------------------------------------------------------------------------
# Surfaceline als CSV exporteren en vakindeling als Shapefile
# Update 9mei2018 - Schrijft uitvoer csv file ook weg aan het vak.
# Update 6juni2018 - Nu is het ook mogelijk om meerdere dwarsprofielen per vak weg te schrijven en shp per vak maar 1 lijnstuk.
# Update 24juli2018 - Werkt vanuit Vakken FC en zoekt niet meer de losse profiel bestanden(SRFVAK_L_* en SRFVAK_P_*) op maar gebruikt het grote totaal bestand.
# --------------------------------------------------------------------------
import string, os, sys, locale, arcpy
# INPUT
VakFC        = sys.argv[1]                 # Lijnen FC met de vakken
IDkol        = "ID"                        # Kolom met id vak
Vkol         = "Vaknaam"                   # Kolom met naam vak
odir         = sys.argv[2]                 # uitvoer map
Kkol         = "SRFpunten"                 # Kolom met type punt
PnmKol       = "PROFIELNAAM"               # kolom met profielnaam tbv def query
Kol          = "RepresentatiefProfiel"     # Representatief kolom
Skol         = "SORTEERVOLGORDE2"          # kolom met de sorteervolgorde van de punten.
Xkol         = "X_WAARDE"
Ykol         = "Y_WAARDE"
Zkol         = "Z_WAARDE"
BGkol        = "LENGTE_TOT_BG"             # lengte van alle punten tot het beginpunt v/h profiel
oCSV_naam    = "Surfacelines.csv"          # de naam van de uitvoer csv
VAK_uitcsv   = "UIT_CSV_Bestand"           # ook aan het vak wegschrijvn waar de csv staat.
PkolVAK      = "REPROF_NAAM"               # kolom aan vakken bestand voor naam representatief profiel.
# databasedir bepalen
workspace1 = os.path.dirname(arcpy.Describe(VakFC).catalogPath)
if [any(ext) for ext in ('.gdb', '.mdb', '.sde') if ext in os.path.splitext(workspace1)]:
    workspace = workspace1
else:
    workspace = os.path.dirname(workspace1) 
arcpy.env.workspace = workspace
#---
arcpy.env.overwriteOutput = True
arcpy.AddMessage("  >>> ----------------------------------")
arcpy.AddWarning("  >>> Wegschrijven surfacelines en vakindeling")
arcpy.AddMessage("  >>> ----------------------------------")
#---------------------------------------------------------
#---------------------------------------------------------
# ----  START
#-------------------------------------------------------
# per vaklijn naam uitlezen, profielnamen selecteren en lijst van maken.
kolommen = ["OID@", "SHAPE@", IDkol, Vkol, VAK_uitcsv, PkolVAK]
# Aantal vakken uitlezen.
count = len(list(i for i in arcpy.da.SearchCursor(VakFC, kolommen)))
arcpy.AddMessage("Aantal vakken: "+str(count))
#-------------------------
with arcpy.da.UpdateCursor(VakFC, kolommen,sql_clause=[None,"ORDER BY "+IDkol]) as Upcursor:
    for Uprow in Upcursor:
        FOUT   = False   # als de benodigde variabelen niet juist zijn dan geen Surfaceline wegschrijven!        
        VakID  = Uprow[2]
        Vnaam  = Uprow[3]
        Reprof = Uprow[5]
        arcpy.AddMessage("\n--------------------------------")
        arcpy.AddMessage("VakID: "+str(VakID))
        arcpy.AddMessage("Naam: "+str(Vnaam))
        arcpy.AddMessage("Representatief profiel: "+str(Reprof))
        #-- De dwarsprofiel FC
        lFC = "PWK_DWARSPROFIEL_LINE"      #"SRFVAK_L_"+VakID
        plFC = "PWK_DWARSPROFIEL_POINT"    #"SRFVAK_P_"+VakID
        arcpy.AddMessage("Surfaceline: "+lFC)
        kolommen = ["SHAPE@XY", Kkol]
        #---------------------------------------------------------
        # Als de FC er niet is dan vak overslaan.
        Lchk = arcpy.Exists(lFC)
        plchk = arcpy.Exists(plFC)
        #---------------------------------------------------------
        # Eerst Surfaceline wegschrijven        
        if Lchk and plchk and FOUT == False and Reprof != None:
            kolommen = ["OID@", "SHAPE@", PnmKol]
            were = PnmKol + " = '" + Reprof + "'"
            # uitlezen.
            try:
                count = len(list(i for i in arcpy.da.SearchCursor(lFC, kolommen, where_clause=were)))
                #arcpy.AddMessage("Aantal dwarsprofielen: "+str(count))
            except:
                #arcpy.AddWarning("  Nog geen representatief profiel gekozen!")
                FOUT = True
            if count == 0:
                arcpy.AddWarning("  is 0!!")
                FOUT = True
            elif count > 1:
                arcpy.AddWarning("  is te veel!!")
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
                # we kunnen meerdere dwarsprofielen hebben bij hetzelfde vak. Dus alleen het profiel van het vaklijnstuk verwerken.
                # Nu naar de punten
                were = PnmKol + " = '"+Reprof+"'"
                XYZlijst = Reprof
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
                    del row2
                    #-------------------------------------------------------------------------------
                    # Open csv file 2 per profiel X_RD;Y_RD;Afstand;Z wegschrijven in een losse file
                    oCSV2_naam = Reprof+".csv"
                    arcpy.AddMessage("Profiel los wegschrijven naar: "+ oCSV2_naam+" ...")
                    if arcpy.Exists(odir+"/"+oCSV2_naam):
                        arcpy.AddMessage("Profiel CSV bestaat al en wordt overschreven!")
                        ll2 = open(odir+"/"+oCSV2_naam, "w")
                    else:
                        arcpy.AddMessage("Profiel CSV aanmaken...")
                        ll2 = open(odir+"/"+oCSV2_naam, "w")
                    # Profiel wegschrijven
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
                # naam en locatie uitvoer CSV aan vak koppelen           
                Uprow[4] = odir+"/"+oCSV_naam    # naam uitvoer CSV aan het bestand koppelen.
                Upcursor.updateRow(Uprow)
#-----------------------------------------------------------------------------------------------
# Als laatste de vakindeling als shape exporteren.
# Hier moeten de dubbele vaklijnen niet in komen te staan dus dubbelingen verwijderen.
# dubbelingen verwijderen
arcpy.AddMessage("\n--------------------------------")
arcpy.AddMessage("Dubbele vakken niet wegschrijven naar uitvoer shape file.")
# eerts kopie maken
arcpy.CopyFeatures_management(VakFC, "in_memory/xxVakken")
# dan unieke vakid lijst maken
IDlijst = []
with arcpy.da.UpdateCursor("in_memory/xxVakken", [IDkol,Vkol]) as cursor2:
    for row2 in cursor2:
        arcpy.AddMessage("Vaknaam: "+str(row2[1]))
        # als ID nog niet voorkomt dan toevoegen.
        lst = set(IDlijst)
        if row2[0] not in lst:
            IDlijst.append(row2[0])
        else:
            # record verwijderen
            arcpy.AddMessage("    > vak verwijderen...")
            cursor2.deleteRow()
# en nu wegschrijven                
arcpy.CopyFeatures_management(in_features="in_memory/xxVakken", out_feature_class=odir+"/Vakindeling_STPH.shp")

arcpy.AddMessage("\n  >>>  KLAAR!  <<<")
