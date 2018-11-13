# -*- coding: cp1252 -*-
# --------------------------------------------------------------------------
# Witteveen+Bos
# ing. H.E.J. Nieuwland - augustus 2018
# --------------------------------------------------------------------------
# versie 1.0.1
# --------------------------------------------------------------------------
# *.prfl tool tbv. toetsing met Ringtoets.
# Uittekenen profiellijn
# 20180523 - optie om ook alle profielen uit te tekenen.
# 20180822 - zowel groene dijk als damwand uittekenen.
# --------------------------------------------------------------------------
import string, os, sys, locale, arcpy, pythonaddins, math
# INPUT
VakFC = sys.argv[1]         # FC met vakken
IDkol = "ID"                # Kolom met id vak Dit is de unieke koppeling tussen vak en prfl file. ID in beide moet gelijk zijn.
Vkol  = "Vaknaam"           # Kolom met naam vak. Vrij in te vullen vaknaam.
Typekol  = "TypeDijk"       # type groene dijk of damwand
VAKv  = sys.argv[2]         # het gekozen vak om te verwerken.
kol   = "PRFLpunten"        # kolom waar het type punt in staat
ckol  = "PRFLcontrole"      # kolom waar controle res in wordt weggeschreven (aanmaken in FME)
Khgt  = "PRFL_KruinHgt"     # de door de gebruiker bepaalde Kruinhoogte incl. eventuele zetting
RUWkols = "Ruw_BuiTal_1","Ruw_BuiTal_2","Ruw_BuiTal_3","Ruw_BuiTal_4","Ruw_BuiTal_5"
HELkols = "PRFL_Helling_1","PRFL_Helling_2","PRFL_Helling_3","PRFL_Helling_4","PRFL_Helling_5"
Alles = sys.argv[3]         # True als we alle vakken willen uittekenen.
#---
objID = 'OBJECTID = '       # kolomnaam van OID om op te selecteren en foutmelding naar juiste punt weg te schrijven.
lay   = os.path.dirname(__file__)+"\\PRFLlijn.lyr"
#---
#---
arcpy.env.overwriteOutput = True
arcpy.AddMessage("  >>> ----------------------------------")
arcpy.AddMessage("  >>> Opbouwen prfl punten ")
arcpy.AddMessage("  >>> ----------------------------------")
#---------------------------------------------------------
#---------------------------------------------------------
# ----  START
#---------------------------------------------------------
arcpy.AddMessage("  Vakken: \n  "+VakFC)
# databasedir bepalen
workspace = os.path.dirname(arcpy.Describe(VakFC).catalogPath)
if [any(ext) for ext in ('.gdb', '.mdb', '.sde') if ext in os.path.splitext(workspace)]:
    workspace = workspace
else:
    workspace = os.path.dirname(workspace)
arcpy.env.workspace = workspace
oDS = workspace+"/PRFL_DATA"
# Eerst vaknaam uitlezen om juiste prfl punten FC te selecteren.
# 2 dan per vak naam uitlezen, profielnamen selecteren en lijst van maken.
Skolommen = ["OID@", "SHAPE@LENGTH", IDkol, Vkol, Khgt, RUWkols[0], RUWkols[1], RUWkols[2], RUWkols[3], RUWkols[4], HELkols[0], HELkols[1], HELkols[2], HELkols[3], HELkols[4], Typekol]
# Aantal vakken uitlezen.
# Als alle vakken moeten worden doorlopen geen query er op!
if Alles == 'true':
    expressie = ''
else:
    expressie = Vkol + " = '" + VAKv + "'"    # punt moet een prfl type hebben.
count = len(list(i for i in arcpy.da.SearchCursor(VakFC, Skolommen, where_clause=expressie)))
arcpy.AddMessage("  Aantal vakken: "+str(count))
HellingVakDict = {}
# -------------------------
with arcpy.da.SearchCursor(VakFC, Skolommen, where_clause=expressie) as cursor:
    for row in cursor:
        erISgeenKOLOM_None = True
        ID = row[2].replace('-','_')
        Zkrn = row[4]
        ruw1 = row[5]
        ruw2 = row[6]
        ruw3 = row[7]
        ruw4 = row[8]
        ruw5 = row[9]
        # als getal dan afronden op 2 decimalen.
        if type(ruw1) == float:
            ruw1 = round(ruw1,2)
        if type(ruw2) == float:
            ruw2 = round(ruw2,2)
        if type(ruw3) == float:
            ruw3 = round(ruw3,2)
        if type(ruw4) == float:
            ruw4 = round(ruw4,2)
        if type(ruw5) == float:
            ruw5 = round(ruw5,2)
        #--
        Xvlnw = None
        vraag = "Yes"
        VAK = str(row[3])
        ProfType = row[15]
        #--
        arcpy.AddMessage("\n  >>> ----------------------------------")
        arcpy.AddMessage("  >>> VakID: "+str(ID))
        arcpy.AddMessage("  >>> ----------------------------------")         
        arcpy.AddMessage("  VakNaam:      "+str(VAK))
        arcpy.AddMessage("  Kruinhoogte:  "+str(round(Zkrn,3))+"m")
        arcpy.AddMessage("  Ruwheden 1-5: "+str(ruw1)+","+str(ruw2)+","+str(ruw3)+","+str(ruw4)+","+str(ruw5))
        arcpy.AddMessage("  Type dijk:    "+str(ProfType)+"\n")
        #---------------------------------------------------------
        if ruw1 == None:
            arcpy.AddError("  >>> Geef minimaal 1 ruwheid op!")
            erISgeenKOLOM_None = False
        if Zkrn == None:
            arcpy.AddError("  >>> De kolom PRFL_KruinHgt van het vak is niet gevuld!")
            erISgeenKOLOM_None = False
        if ruw1 == None or ruw2 == None or ruw3 == None or ruw4 == None or ruw5 == None:
            arcpy.AddWarning("  >>> Let op: Niet alle 5 ruwheid kolommen zijn gevuld!\n      Als je meerdere talud segmenten hebt moet je deze invullen anders worden ze op 1 gezet.")
        #---------------------------------------------------------
        # dict maken 
        RUW = {}
        t = 0        
        while t <= 4:
            wrd = eval("ruw"+str(t+1))
            if wrd == None:
                wrd = 1
            RUW[t] = wrd
            t += 1
        #arcpy.AddMessage(" RUW: "+ str(RUW))
        #--
        if erISgeenKOLOM_None:
            #  profielpunten selecteren en toevoegen.
            Pnm = "PRFL_P_"+ID
            Pshp = oDS+"/"+Pnm
            Lnm = "Lvak_"+ID
            Lshp = oDS+"/"+Lnm
            #---------------------------------------------------------
            # Als de FC er niet is dan vak overslaan.
            Pchk = arcpy.Exists(Pnm)
            Lchk = arcpy.Exists(Pnm)
            #---------------------------------------------------------
            if Pchk and Lchk:
                # Create cursor for feature class
                # Create an expression
                expression = kol + " LIKE '%_prfl'"    # punt moet een prfl type hebben.
                nr = 0
                kolommen = ["SHAPE@X", "SHAPE@Y", kol, ckol, "OID@"]
                # -------------------------
                # totaal aantal bepalen
                count = len(list(i for i in arcpy.da.SearchCursor(Pshp, kolommen, where_clause=expression)))
                arcpy.AddMessage("  > Totaal aantal punten:  "+str(count))
                # -------------------------
                # Als er prfl punten zijn dan verwerken
                if count > 0:
                    # aantallen bepalen en XZ uitlezen
                    #XZall = []
                    XZvoorl = []
                    XZteen = []
                    XZdamw = []
                    XZkruin = []
                    XZtaludk = []
                    hellijst = []
                    # -------------------------
                    with arcpy.da.UpdateCursor(Pshp, kolommen, where_clause=expression) as cursor2:
                        for row2 in cursor2:
                            nr = nr + 1
                            naam = row2[2]
                            # Punt toevoegen aan de totaal array
                            #XZall.append([round(row2[0],3),round(row2[1],3),row2[4]])
                            # even kijken welk type punt we hebben en XZ vastleggen
                            # Voorland
                            if (naam == "Voorland_prfl"):
                                XZvoorl.append([round(row2[0],3),round(row2[1],3),row2[4]])
                            elif (naam == "Buitenteen_prfl"):
                                XZteen.append([round(row2[0],3),round(row2[1],3),row2[4]])
                            elif (naam == "Damwand_prfl"):
                                XZdamw.append([round(row2[0],3),round(row2[1],3),row2[4]])
                            elif (naam == "Buitenkruin_prfl"):
                                arcpy.AddMessage("  Zkruin is: "+str(round(row2[1],2))+"m")
                                # Z Buitenkruin direct vervangen door Z gebruiker van het vak
                                row2[1] = Zkrn
                                cursor2.updateRow(row2)
                                arcpy.AddMessage("  Zkruin wordt: "+str(round(row2[1],3))+"m")
                                XZkruin.append([round(row2[0],3),round(row2[1],3),row2[4]])
                            elif (naam == "Taludknik_prfl"):
                                XZtaludk.append([round(row2[0],3),round(row2[1],3),row2[4]])
                            else:
                                arcpy.AddWarning("  > onbekend punt! : "+naam)
                    del row2, cursor2
                    # Nu de aantallen controleren
                    # Voorland
                    arcpy.AddMessage("  > n voorland:            "+str(len(XZvoorl)))
                    if len(XZvoorl) < 1:
                        arcpy.AddWarning("    minimaal 1 voorland punt nodig!")
                    # Damwand
                    arcpy.AddMessage("  > n teen:                "+str(len(XZteen)))
                    arcpy.AddMessage("  > n taludknikpunt:       "+str(len(XZtaludk)))
                    arcpy.AddMessage("  > n damwand:             "+str(len(XZdamw)))
                    arcpy.AddMessage("  > n kruin:               "+str(len(XZkruin)))
                    if ProfType == "damwand":
                        if len(XZdamw) == 1:
                            arcpy.AddMessage("    1 damwandpunt!\n dus geen kruin of teen nodig.")
                        elif len(XZdamw) > 1:
                            arcpy.AddError("    meer dan 1 damwandpunt!")
                            Err = True
                    elif ProfType == "groene dijk":
                        # BuitenTeen                    
                        if len(XZteen) > 1:
                            arcpy.AddWarning("    meer dan 1 teen punt!")
                        if len(XZteen) < 1:
                            arcpy.AddError("    minimaal 1 teen punt nodig!")
                        # BuitenKruin
                        if len(XZkruin) > 1:
                            arcpy.AddWarning("    meer dan 1 kruin punt!")
                        if len(XZkruin) < 1:
                            arcpy.AddError("    minimaal 1 kruin punt nodig!")
                        # Talud knikpunt (max 4 punten)
                        if len(XZtaludk) > 4:
                            arcpy.AddWarning("    meer dan 4 Taludknikpunten!")
                    arcpy.AddMessage("  >")
                    # -------------------------
                    # Nu de PRFL lijn uittekenen.
                    # Lege FC aanmaken
                    PRFL_ln = "PRFL_lijn_"+ID                                                     # LET OP deze naam wordt ook in 3 Sel Profielen per vak gebruikt!
                    try:
                        arcpy.CreateFeatureclass_management(oDS, PRFL_ln, "POLYLINE")
                    except:
                        arcpy.AddError("xx Kan de lijnen FC niet aanmaken! Stop de edit sessie!!")
                        sys.exit()
                    try:
                        arcpy.AddField_management(PRFL_ln, "PRFL_Ruwheid", "DOUBLE")
                    except:
                        arcpy.AddError("Kolom PRFL_Ruwheid bestaat al!")
                    try:
                        arcpy.AddField_management(PRFL_ln, "PRFL_Helling", "DOUBLE")
                    except:
                        arcpy.AddError("Kolom PRFL_Helling bestaat al!")
                    INkolommen = ["SHAPE@","PRFL_Ruwheid","PRFL_Helling"]
                    # -------------------------
                    # nu elk los segmentje uittekenen begin vanaf de kruin.
                    # cursor openen
                    insert_cursor = arcpy.da.InsertCursor(oDS+"/"+PRFL_ln,INkolommen)
                    # punten toevoegen
                    array = arcpy.Array()
                    point1 = arcpy.Point()
                    point2 = arcpy.Point()
                    if ProfType == "groene dijk":
                        # punten lijsten sorteren
                        XZtaludk = sorted(XZtaludk,reverse=True)
                        XZvoorl = sorted(XZvoorl,reverse=True)
                        # de kruin
                        point1.X = XZkruin[0][0]
                        point1.Y = Zkrn
                        # door de taludpunten loopen indien ze aanwezig zijn.
                        n = 0                    
                        if len(XZtaludk)> 0:
                            while n <= len(XZtaludk) - 1:
                                point2.X = XZtaludk[n][0]
                                point2.Y = XZtaludk[n][1]
                                array.add(point1)
                                array.add(point2)
                                # helling bepalen
                                dtx = point2.X - point1.X
                                dtz = point2.Y - point1.Y
                                hel = round((dtx / dtz), 2)  #op 2 decimalen
                                hellijst.append(hel)
                                arcpy.AddMessage("  > helling:               "+str(hel))
                                # Nu punten array aan polyline toe voegen en inserten.
                                polyline=arcpy.Polyline(array)
                                array.removeAll()
                                insert_cursor.insertRow([polyline,RUW.get(n),hel])
                                point1.X = point2.X
                                point1.Y = point2.Y
                                arcpy.AddMessage("  > Ruwheid nr: "+str(n)+" :        "+str(RUW.get(n)))
                                n += 1
                        # afsluiten met de teen of meteen van kruin naar teen.
                        point2.X = XZteen[0][0]
                        point2.Y = XZteen[0][1]
                        array.add(point1)
                        array.add(point2)
                        # helling bepalen
                        dtx = point2.X - point1.X
                        dtz = point2.Y - point1.Y
                        hel = round((dtx / dtz), 2)     #op 2 decimalen
                        hellijst.append(hel)
                        arcpy.AddMessage("  > helling:               "+str(hel))
                        # Nu punten array aan polyline toe voegen en inserten.
                        polyline=arcpy.Polyline(array)
                        array.removeAll()
                        insert_cursor.insertRow([polyline,RUW.get(n),hel])
                        arcpy.AddMessage("  > Ruwheid naar de teen nr: "+str(n)+" :        "+str(RUW.get(n)))
                        point1.X = point2.X
                        point1.Y = point2.Y
                        #---
                        # en door met het voorland is altijd minimaal 1 punt aanwezig.
                        n = 0
                        while n <= len(XZvoorl) - 1:
                            point2.X = XZvoorl[n][0]
                            point2.Y = XZvoorl[n][1]
                            array.add(point1)
                            array.add(point2)
                            # helling bepalen
                            dtx = point2.X - point1.X
                            dtz = point2.Y - point1.Y
                            hel = round((dtx / dtz), 2)  #op 2 decimalen
                            arcpy.AddMessage("  > helling:               "+str(hel))
                            # Nu punten array aan polyline toe voegen en inserten.
                            polyline=arcpy.Polyline(array)
                            array.removeAll()
                            insert_cursor.insertRow([polyline,0,hel])
                            point1.X = point2.X
                            point1.Y = point2.Y
                            n += 1
                        #----------------------------------------        
                        # de hellinglijst op volorde wegschrijven naar de 5 kolommen aan het vak. indien minder waarden de rest op NULL zetten
                        # eerst even alle kolommen op NULL zetten en daarna vullen met de hellijst.
                        l = len(hellijst)+1
                        while l <= 5:
                            hellijst.append(None)
                            l += 1
                        HellingVakDict[ID] = hellijst
                    #----------------------------------------
                    elif ProfType == "damwand":
                        # punten lijsten sorteren
                        XZvoorl = sorted(XZvoorl,reverse=True)
                        # de kruin
                        point1.X = XZdamw[0][0]
                        point1.Y = Zkrn
                        # afsluiten met de teen of meteen van kruin naar teen.
                        point2.X = XZdamw[0][0]
                        point2.Y = XZdamw[0][1]
                        array.add(point1)
                        array.add(point2)
                        # helling bepalen
                        dtx = point2.X - point1.X
                        dtz = point2.Y - point1.Y
                        hel = round((dtx / dtz), 2)     #op 2 decimalen
                        hellijst.append(hel)
                        arcpy.AddMessage("  > helling:               "+str(hel))
                        # Nu punten array aan polyline toe voegen en inserten.
                        polyline=arcpy.Polyline(array)
                        array.removeAll()
                        insert_cursor.insertRow([polyline,1,hel])
                        arcpy.AddMessage("  > Ruwheid naar de teen nr:    "+str(1))
                        point1.X = point2.X
                        point1.Y = point2.Y
                        #---
                        # en door met het voorland is altijd minimaal 1 punt aanwezig.
                        n = 0
                        while n <= len(XZvoorl) - 1:
                            point2.X = XZvoorl[n][0]
                            point2.Y = XZvoorl[n][1]
                            array.add(point1)
                            array.add(point2)
                            # helling bepalen
                            dtx = point2.X - point1.X
                            dtz = point2.Y - point1.Y
                            hel = round((dtx / dtz), 2)  #op 2 decimalen
                            arcpy.AddMessage("  > helling:               "+str(hel))
                            # Nu punten array aan polyline toe voegen en inserten.
                            polyline=arcpy.Polyline(array)
                            array.removeAll()
                            insert_cursor.insertRow([polyline,1,hel])
                            point1.X = point2.X
                            point1.Y = point2.Y
                            n += 1
                    #----------------------------------------
                    # Lijn toevoegen aan TOC
                    MXD  = arcpy.mapping.MapDocument("CURRENT")
                    DF   = arcpy.mapping.ListDataFrames(MXD)[0]
                    lyr1 = arcpy.mapping.Layer(lay)
                    lyr1.replaceDataSource(workspace,"FILEGDB_WORKSPACE",PRFL_ln)
                    lyr1.name = "PRFL_lijn_"+str(ID)
                    if arcpy.Exists(VAK):
                        arcpy.AddMessage("  Aan bestaande grouplayer toevoegen!")
                        grplyr = arcpy.mapping.ListLayers(MXD, VAK, DF)[0]
                        arcpy.mapping.AddLayerToGroup(DF,grplyr,lyr1,"TOP")
                    else:
                        arcpy.mapping.AddLayer(DF, lyr1, "TOP")
                    #---
                    del insert_cursor, polyline, point1, point2
                else:
                    arcpy.AddWarning("  Geen PRFL punten ingetekend voor dit vak!")
            else:
                arcpy.AddWarning("  PRFL FC's van dit vak bestaan niet!")
#----------------------------------------
# Als er PRFL lijnen zijn uitgetekend dan de hellingen nog wegschrijven aan het vakken bestand. ivm meerdere cursors buiten de loop gehaald.
# dmv HellingVakDict
if len(HellingVakDict) > 0:
    with arcpy.da.UpdateCursor(VakFC, Skolommen) as cursor:
        for row in cursor:
            ID = row[2].replace('-','_')
            Hlijst = HellingVakDict.get(ID)
            if Hlijst:
                row[10] = Hlijst[0]
                row[11] = Hlijst[1]
                row[12] = Hlijst[2]
                row[13] = Hlijst[3]
                row[14] = Hlijst[4]
                cursor.updateRow(row)
            Hlijst = ''
#----------------------------------------
arcpy.AddMessage("\n  >>> KLAAR! <<<\n")
