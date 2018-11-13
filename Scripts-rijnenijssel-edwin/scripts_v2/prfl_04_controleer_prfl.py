# --------------------------------------------------------------------------
# Witteveen+Bos
# ing. H.E.J. Nieuwland - augustus 2018
# --------------------------------------------------------------------------
# versie 1.0.1
# --------------------------------------------------------------------------
# *.prfl tool tbv. toetsing met Ringtoets.
# Voorland: kan uit meerdere punten bestaan. Tot een max van 5 punten!!
# Damwand kan nog niet in Ringtoets. Dus altijd 0 punten.
# Teen mag er maar 1 zijn ingetekend
# Kruin mag we ook maar 1 puntzijn.
# Toe te passen uitgangspunten:
#  o	Taluddelen dijk: 1:8 tot 1:1
#  o	Bermdelen dijk: 1:100 tot 1:15
#  o	de hoogte van de taluddeel punten moet oplopen vanaf de teen naar de kruin
#  o	maximaal 2 bermen, waarbij de berm wel mag bestaan uit opeenvolgende bermdelen
#  o	het laagste en hoogste profieldeel sluit aan op teen respectievelijk buitenkruin, beiden zijn taluddelen
#  o	afstand tussen de dijkpunten niet te klein. > 2m
#  o	voorland niet steiler dan 1:10(horizontaal of negatief mag ook)
#  o	voorlandpunten > 10m uit elkaar. (niet te veel detail)
#  o	hoogtes voorlandpunten altijd hoger dan hoogte van het eerste voorlandpunt.
# --------------------------------------------------------------------------
# update
# 20180822  -   Nu ook controle als het type een damwand is.
# --------------------------------------------------------------------------
import string, os, sys, locale, arcpy
# INPUT
VakFC    = sys.argv[1]         # Vakken FC van waaruit het te controleren wordt geselecteerd
Vaknaam  = sys.argv[2]         # Vaknaam uit het vakken bestand
Khgt     = "PRFL_KruinHgt"     # de door de gebruiker bepaalde Kruinhoogte incl. eventuele zetting
IDkol    = "ID"                # Kolom met id vak Dit is de unieke koppeling tussen vak en prfl file. ID in beide moet gelijk zijn.
Vkol     = "Vaknaam"           # Kolom met naam vak. Vrij in te vullen vaknaam.
Typekol  = "TypeDijk"          # type groene dijk of damwand 
kol      = "PRFLpunten"        # kolom waar het type punt in staat
ckol     = "PRFLcontrole"      # kolom waar controle res in wordt weggeschreven (aanmaken in FME)
#---
objID    = 'OBJECTID = '       # kolomnaam van OID om op te selecteren en foutmelding naar juiste punt weg te schrijven. 
kolommen = ["SHAPE@X", "SHAPE@Y", kol, ckol, "OID@"]
#---
arcpy.env.overwriteOutput = True
arcpy.AddMessage("  >>> ----------------------------------")
arcpy.AddWarning("  >>> Controleren prfl punten ")
arcpy.AddMessage("  >>> ----------------------------------")
#---------------------------------------------------------
#---------------------------------------------------------
# ----  START
#---------------------------------------------------------
def SchrijfError(expr,melding):
    with arcpy.da.UpdateCursor(Pshp, kolommen, where_clause=expr) as cursor:
        row = cursor.next()
        waarde = row[3]
        if waarde != 'ok':
            melding = waarde+" / "+melding
        row[3] = melding
        cursor.updateRow(row)
    del row, cursor
    return(True)
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
Skolommen = ["OID@", "SHAPE@LENGTH", IDkol, Vkol, Khgt, Typekol]
# Het vak uitlezen.
expressie = Vkol + " = '" + Vaknaam + "'"    # punt moet een prfl type hebben.
count = len(list(i for i in arcpy.da.SearchCursor(VakFC, Skolommen, where_clause=expressie)))
# -------------------------
with arcpy.da.SearchCursor(VakFC, Skolommen, where_clause=expressie) as Scursor:
    for Srow in Scursor:
        ID = Srow[2].replace('-','_')
        Zkrn = Srow[4]
        VAK = str(Srow[3])
        ProfType = Srow[5]
        #--
        arcpy.AddMessage("\n  >>> ----------------------------------")
        arcpy.AddMessage("  >>> VakID: "+str(ID))
        arcpy.AddMessage("  >>> ----------------------------------")         
        arcpy.AddMessage("  VakNaam:      "+str(VAK))
        arcpy.AddMessage("  Kruinhoogte:  "+str(round(Zkrn,2))+"m")
        arcpy.AddMessage("  Type dijk:    "+str(ProfType)+"\n")
        #---------------------------------------------------------
#---------------------------------------------------------
#  profielpunten selecteren.
Pnm = "PRFL_P_"+ID
Pshp = oDS+"/"+Pnm
#---------------------------------------------------------
# Als de FC er niet is dan vak overslaan.
Pchk = arcpy.Exists(Pnm)
#---------------------------------------------------------
if Pchk:
    ##### Zorgen dat er geen selectie op de laag zit.
    #####arcpy.SelectLayerByAttribute_management(Pshp,"CLEAR_SELECTION")
    # Create update cursor for feature class
    # Create an expression
    expression = kol + " LIKE '%_prfl'"    # punt moet een prfl type hebben.
    nr = 0
    # -------------------------
    # aantallen bepalen en XZ uitlezen
    XZall = []
    XZvoorl = []
    XZteen = []
    XZdamw = []
    XZkruin = []
    XZtaludk = []
    Err = False
    # totaal
    count = len(list(i for i in arcpy.da.SearchCursor(Pshp, kolommen, where_clause=expression)))
    arcpy.AddMessage("  > Totaal aantal punten:  "+str(count))
    arcpy.AddMessage("  >")
    # -------------------------
    with arcpy.da.UpdateCursor(Pshp, kolommen, where_clause=expression) as cursor:
        for row in cursor:
            nr = nr + 1
            naam = row[2]
            # Punt toevoegen aan de totaal array
            XZall.append([round(row[0],3),round(row[1],3),row[4]])
            # even kijken welk type punt we hebben en XZ vastleggen
            # Voorland
            if (naam == "Voorland_prfl"):
                XZvoorl.append([round(row[0],3),round(row[1],3),row[4]])
            elif (naam == "Buitenteen_prfl"):
                XZteen.append([round(row[0],3),round(row[1],3),row[4]])
            elif (naam == "Damwand_prfl"):
                XZdamw.append([round(row[0],3),round(row[1],3),row[4]])
            elif (naam == "Buitenkruin_prfl"):
                XZkruin.append([round(row[0],3),round(Zkrn,3),row[4]])     # Kruin moet Z krijgen uit kolom van Vak.
            elif (naam == "Taludknik_prfl"):
                XZtaludk.append([round(row[0],3),round(row[1],3),row[4]])
            else:
                arcpy.AddWarning("  > onbekend punt! : "+naam)
            # opmerking bij punt wegschrijven.
            row[3] = "ok"   
            cursor.updateRow(row)
    # Nu de aantallen controleren
    # Voorland
    arcpy.AddMessage("  > n voorland:            "+str(len(XZvoorl)))
    if len(XZvoorl) < 1:
        arcpy.AddError("    minimaal 1 voorland punt nodig!")
        Err = True
    # Damwand
    arcpy.AddMessage("  > n damwand:             "+str(len(XZdamw)))
    arcpy.AddMessage("  > n teen:                "+str(len(XZteen)))
    arcpy.AddMessage("  > n taludknikpunt:       "+str(len(XZtaludk)))
    arcpy.AddMessage("  > n kruin:               "+str(len(XZkruin)))
    if ProfType == "damwand":
        if len(XZdamw) == 1:
            arcpy.AddMessage("    1 damwandpunt!\n      dus geen kruin of teen nodig.")
        elif len(XZdamw) > 1:
            arcpy.AddError("    meer dan 1 damwandpunt!")
            Err = True
        elif len(XZdamw) < 1:
            arcpy.AddError("    geen damwandpunt!")
            Err = True
    elif ProfType == "groene dijk":
        # BuitenTeen
        if len(XZteen) > 1:
            arcpy.AddError("    meer dan 1 teen punt!")
            Err = True
        if len(XZteen) < 1:
            arcpy.AddError("    minimaal 1 teen punt nodig!")
            Err = True
        # BuitenKruin
        if len(XZkruin) > 1:
            arcpy.AddError("    meer dan 1 kruin punt!")
            Err = True
        if len(XZkruin) < 1:
            arcpy.AddError("    minimaal 1 kruin punt nodig!")
            Err = True
        # Talud knikpunt (max 4 punten)
        if len(XZtaludk) > 4:
            arcpy.AddError("    meer dan 4 Taludknikpunten!")
            Err = True
    else:
        Err = True
    arcpy.AddMessage("  >")
    # taludpunten sorteren
    XZtaludk = sorted(XZtaludk)
    # voorlandpunten sorteren
    XZvoorl = sorted(XZvoorl)
    # alle punten sorteren
    XZall = sorted(XZall)
    #------------------------------------------------
    # als alle punten zijn doorlopen dan verder.
    #------------------------------------------------
    #----------------------------------------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------------------------------------
    if ProfType == "groene dijk" and not Err:
        # Nu controleren
        #---------------------------------------------------------
        # ----  Controle: Simpele check ----
        #---------------------------------------------------------
        arcpy.AddMessage("  >>> ----------------------------------")
        arcpy.AddMessage("  >>> Controleren puntvolgorde groene dijk profiel...")
        #----------------------------------------
        # Controleren of Z kruin de grootste is en er geen punten verkeerd liggen
        # Voorlandpunten voor de Teen en taludpunten tussen teen en kruin. Z van alle punten < Z kruin. 
        #----------------------------------------
        # alle punten moeten lager of gelijk aan de buitenkruin+ zijn.
        for zp in XZall:
            # Z vd kruin is in XZall niet de ingevoerde Z maar de ingeklikte Z en dus niet juist. punt uitsluiten bij deze check.
            if zp[1] > XZkruin[0][1] and [zp[0],zp[2]] != [XZkruin[0][0],XZkruin[0][2]]:
                expr = objID + str(zp[2])
                melding = "Profielpunt ligt hoger dan de Kruin!"
                arcpy.AddError("      "+melding)
                Err = SchrijfError(expr,melding)
        # voorland voor de teen
        if len(XZvoorl) > 0 and len(XZteen) == 1:
            for xz in XZvoorl:
                if xz[0] > XZteen[0][0]:
                    expr = objID + str(xz[2])
                    melding = "voorland punt ligt voorbij de buitenteen!"
                    arcpy.AddError("      "+melding)
                    Err = SchrijfError(expr,melding)
                if xz[1] < XZvoorl[0][1]:
                    expr = objID + str(xz[2])
                    melding = "voorland punt is lager dan 1e voorlandpunt!"
                    arcpy.AddError("      "+melding)
                    Err = SchrijfError(expr,melding)
            if XZvoorl[0][1] > XZteen[0][1]:
                expr = objID + str(XZteen[0][2])
                melding = "Teen punt is lager dan 1e voorlandpunt!"
                arcpy.AddError("      "+melding)
                Err = SchrijfError(expr,melding)
        if len(XZtaludk) > 0 and len(XZkruin) == 1:
            for xz in XZtaludk:
                if xz[0] > XZkruin[0][0]:
                    expr = objID + str(xz[2])
                    melding = "taludknikpunt ligt voorbij de Kruin!"
                    arcpy.AddError("      "+melding)
                    Err = SchrijfError(expr,melding)
                elif xz[0] < XZteen[0][0]:
                    expr = objID + str(xz[2])
                    melding = "taludknikpunt ligt voor de buitenteen!"
                    arcpy.AddError("      "+melding)
                    Err = SchrijfError(expr,melding)
        if len(XZkruin) == 1 and len(XZteen) == 1:
            if XZteen[0][0] > XZkruin[0][0]:
                expr = objID + str(XZteen[0][2])
                melding = "Teen punt ligt voorbij de Kruin!"
                arcpy.AddError("      "+melding)
                Err = SchrijfError(expr,melding)
        #---------------------------------------------------------
        # ----  Controle: TEEN naar KRUIN ----
        #---------------------------------------------------------
        arcpy.AddMessage("  >>> ----------------------------------")
        arcpy.AddMessage("  >>> Controleren Teen -> Kruin...")
        XZteenkruin = []
        XZteenkruin.append(XZteen[0])
        for pnt in XZtaludk:
            XZteenkruin.append(pnt)
        XZteenkruin.append(XZkruin[0])
        # nu X > 2m, helling en Z oplopend controleren
        nr_taluddeel = 0
        n_taludbermen = 0
        for pnt in XZteenkruin:    
            nr_taluddeel += 1
            arcpy.AddMessage("\n      nr_taluddeel:         "+str(nr_taluddeel))
            arcpy.AddMessage("      Puntnummer(oid):         "+str(pnt[2])+"  X: "+str(pnt[0])+"m  "+"  Z: "+str(pnt[1])+"m")
            # 1e punt
            if pnt[2] == XZteen[0][2]:
                Xp0 = XZteen[0][0]
                Zp0 = XZteen[0][1]
            else:
                Zp = pnt[1]
                Xp = pnt[0]
                if Zp < Zp0:
                    # punt selecteren in de cursor en opmerking bij punt wegschrijven.
                    expr = objID + str(pnt[2])
                    melding = "Z taludpunt lager dan voorgaand punt!"
                    Err = SchrijfError(expr,melding)
                    arcpy.AddError("      "+melding+", "+str(Zp)+"m < "+str(Zp0)+"m")
                dtx = Xp - Xp0
                dtz = Zp - Zp0
                arcpy.AddMessage("      afstand:  horizontaal:   "+str(dtx)+"m"+"  /  verticaal:  "+str(dtz)+"m")
                if dtx < 2:
                    # punt selecteren in de cursor en opmerking bij punt wegschrijven.
                    expr = objID + str(pnt[2])
                    melding = "Taludpunten liggen te dicht bij elkaar!"
                    Err = SchrijfError(expr,melding)
                    arcpy.AddError("      "+melding+" "+str(dtx)+"m\n"+"      "+"Moeten minimaal 2m uit elkaar liggen.")
                # helling controleren
                Hk1 = round((dtx / dtz), 2)  #op 2 decimalen
                arcpy.AddMessage("      helling:                 "+str(Hk1))
                # check of taluddeel bermdeel is? max. 2 stuks.
                if (nr_taluddeel == 2 or nr_taluddeel == 6):
                    if (nr_taluddeel == 2):
                        arcpy.AddMessage("      1e Taluddeel.")
                    elif (nr_taluddeel == 6):
                        arcpy.AddMessage("      5e Taluddeel.")
                if (Hk1 >= 15.0 and Hk1 <= 100.0 and nr_taluddeel in [1,3,4,5]):
                    arcpy.AddMessage("      Bermdeel!")
                    n_taludbermen += 1
                    # mogen maar 2 bermen zijn
                    if n_taludbermen > 2:
                        # punt selecteren in de cursor en opmerking bij punt wegschrijven.
                        expr = objID + str(pnt[2])
                        melding = "Meer dan 2 bermen niet mogelijk!"
                        arcpy.AddError("      "+melding)
                        Err = SchrijfError(expr,melding)
                    else:
                        arcpy.AddMessage("      > OK")
                elif (Hk1 <= 1.0 or Hk1 >= 8.0):
                    # punt selecteren in de cursor en opmerking bij punt wegschrijven.
                    expr = objID + str(pnt[2])
                    melding = "Taludhelling niet tussen 1:1 en 1:8 of > 1:15!"
                    arcpy.AddError("      "+melding)
                    Err = SchrijfError(expr,melding)
                else:
                    arcpy.AddMessage("      > OK")
                # punt doorschuiven naar 1e punt tbv check volgend punt.
                Xp0 = Xp
                Zp0 = Zp
                arcpy.AddMessage("      -------")
        #---------------------------------------------------------
        # ----  Controle: VOORLAND naar TEEN ----
        #---------------------------------------------------------
        arcpy.AddMessage("  >>> ----------------------------------")
        arcpy.AddMessage("  >>> Controleren Voorland -> Teen...")
        XZvoorlteen = XZvoorl
        XZvoorlteen.append(XZteen[0])
        if len(XZvoorlteen) > 1:
            for pnt in XZvoorlteen:    
                arcpy.AddMessage("\n      Puntnummer(oid):         "+str(pnt[2])+"  X: "+str(pnt[0])+"m  "+"  Z: "+str(pnt[1])+"m")
                # 1e punt
                if pnt[2] == XZvoorl[0][2]:
                    Xp0 = XZvoorl[0][0]
                    Zp0 = XZvoorl[0][1]
                else:
                    Zp = pnt[1]
                    Xp = pnt[0]
                    dtx = Xp0 - Xp
                    dtz = Zp0 - Zp
                    arcpy.AddMessage("      afstand:  horizontaal:   "+str(dtx)+"m"+"  /  verticaal:  "+str(dtz)+"m")
                    if abs(dtx) < 10:
                        # punt selecteren in de cursor en opmerking bij punt wegschrijven.
                        expr = objID + str(pnt[2])
                        melding = "Voorlandpunten liggen te dicht bij elkaar!"
                        Err = SchrijfError(expr,melding)
                        arcpy.AddError("      "+melding+" "+str(abs(dtx))+"m\n"+"      "+"Moeten minimaal 10m uit elkaar liggen.")
                    # helling controleren
                    Hk = round((dtx / dtz), 2)  #op 2 decimalen
                    arcpy.AddMessage("      helling:                 "+str(Hk))
                    if (abs(Hk) < 10.0):
                        # punt selecteren in de cursor en opmerking bij punt wegschrijven.
                        expr = objID + str(pnt[2])
                        melding = "Voorlandhelling te steil! maximaal 1:10"
                        arcpy.AddError("      "+melding)
                        Err = SchrijfError(expr,melding)
                    else:
                        arcpy.AddMessage("      > OK")
                    # punt doorschuiven naar 1e punt tbv check volgend punt.
                    Xp0 = Xp
                    Zp0 = Zp
                    arcpy.AddMessage("      -------")
        else:
            arcpy.AddWarning("      geen voorlandpunten aanwezig.")
    #----------------------------------------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------------------------------------
    elif ProfType == "damwand" and not Err:
        # Nu controleren
        #---------------------------------------------------------
        # ----  Controle: Simpele check ----
        #---------------------------------------------------------
        arcpy.AddMessage("  >>> ----------------------------------")
        arcpy.AddMessage("  >>> Controleren puntvolgorde damwand profiel...")
        #----------------------------------------
        # Bij een damwand hebben we alleen voorland punten en 1 damwandpunt(onderkant bodem damwand)
        # Controleren of Z van de punten > is dan het 1e voorlandpunt
        # Voorlandpunten mogen niet binnenwaarts van het damwandpunt liggen. 
        #----------------------------------------
        # voorland voor de damwand
        if len(XZvoorl) > 0 and len(XZdamw) == 1:
            for xz in XZvoorl:
                if xz[0] > XZdamw[0][0]:
                    expr = objID + str(xz[2])
                    melding = "voorland punt ligt binnenwaarts van de damwand!"
                    arcpy.AddError("      "+melding)
                    Err = SchrijfError(expr,melding)
                if xz[1] < XZvoorl[0][1]:
                    expr = objID + str(xz[2])
                    melding = "voorland punt is lager dan 1e voorlandpunt!"
                    arcpy.AddError("      "+melding)
                    Err = SchrijfError(expr,melding)
        #---------------------------------------------------------
        # ----  Controle: VOORLAND naar TEEN ----
        #---------------------------------------------------------
        arcpy.AddMessage("  >>> ----------------------------------")
        arcpy.AddMessage("  >>> Controleren Voorland -> Damwand...")
        XZvoorldamw = XZvoorl
        XZvoorldamw.append(XZdamw[0])
        if len(XZvoorldamw) > 1:
            for pnt in XZvoorldamw:    
                arcpy.AddMessage("\n      Puntnummer(oid):         "+str(pnt[2])+"  X: "+str(pnt[0])+"m  "+"  Z: "+str(pnt[1])+"m")
                # 1e punt
                if pnt[2] == XZvoorl[0][2]:
                    Xp0 = XZvoorl[0][0]
                    Zp0 = XZvoorl[0][1]
                else:
                    Zp = pnt[1]
                    Xp = pnt[0]
                    dtx = Xp0 - Xp
                    dtz = Zp0 - Zp
                    arcpy.AddMessage("      afstand:  horizontaal:   "+str(dtx)+"m"+"  /  verticaal:  "+str(dtz)+"m")
                    if abs(dtx) < 10:
                        # punt selecteren in de cursor en opmerking bij punt wegschrijven.
                        expr = objID + str(pnt[2])
                        melding = "Voorlandpunten liggen te dicht bij elkaar!"
                        Err = SchrijfError(expr,melding)
                        arcpy.AddError("      "+melding+" "+str(abs(dtx))+"m\n"+"      "+"Moeten minimaal 10m uit elkaar liggen.")
                    # helling controleren
                    Hk = round((dtx / dtz), 2)  #op 2 decimalen
                    arcpy.AddMessage("      helling:                 "+str(Hk))
                    if (abs(Hk) < 10.0):
                        # punt selecteren in de cursor en opmerking bij punt wegschrijven.
                        expr = objID + str(pnt[2])
                        melding = "Voorlandhelling te steil! maximaal 1:10"
                        arcpy.AddError("      "+melding)
                        Err = SchrijfError(expr,melding)
                    else:
                        arcpy.AddMessage("      > OK")
                    # punt doorschuiven naar 1e punt tbv check volgend punt.
                    Xp0 = Xp
                    Zp0 = Zp
                    arcpy.AddMessage("      -------")
        else:
            arcpy.AddWarning("      geen voorlandpunten aanwezig.")
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
arcpy.AddWarning("\n  >>> ----------------------------------")
if Err:
    arcpy.AddWarning("  >>> Alle "+str(len(XZall))+" punten gecontroleerd!\n")
    arcpy.AddError("      -- Fouten gevonden!! --")
else:
    arcpy.AddWarning("  >>> Alle "+str(len(XZall))+" punten gecontroleerd!\n")
    arcpy.AddWarning("  >>> Alles OK!")
arcpy.AddMessage("  >>> ----------------------------------")
arcpy.AddWarning("\n  >>> KLAAR! <<<\n")
