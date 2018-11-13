# --------------------------------------------------------------------------
# Witteveen+Bos
# ing. H.E.J. Nieuwland - mei 2018
# --------------------------------------------------------------------------
# versie 1.0.2
# --------------------------------------------------------------------------
# Bepaal van gekozen representatief profiel het snijpunt met de piping in en uit trede lijnen.
# orientatie afstand tot snijpunt vanaf begin profiellijn buitenwaarts.
# HRD koppeling obv dwarsprofiellijn(midpoint)
# 20180529 - XML_VerwachtingswaardePolderpeil toegevoegd
# 20180718 - HRD optie wel of niet bepalen.
# --------------------------------------------------------------------------
import string, os, sys, locale, arcpy
# INPUT
VakFC       = sys.argv[1]                 # Vakken FC
uitKOL      = sys.argv[2]                 # Kolom aan de Vakken FC waar de afstand in wordt weggeschreven
pipFC       = sys.argv[3]                 # FC met 1 piping intrede of uittrede lijn. 
LnmKol      = "PROFIELNAAM"               # kolom met profielnaam
Tkol        = "TYPE"                      # Binnentalud of Buitentalud
HRDfc       = sys.argv[4]                 # HRD locaties
HRDkol_org  = "Name"                      # kolom in HRD bestand met de naam van de HRD locatie
HRDkol      = "HRD_Name"                  # Kolom in VakFC waar de HRD naam in moet komen.
HRD_jn      = sys.argv[5]                 # HRD wel of niet updaten
VAKkols     = "REPROF_NAAM",uitKOL,"ID",HRDkol,"XML_VerwachtingswaardePolderpeil", "Aandachtspunten", "X0"   # kolommen aan vakken bestand.
VW          = sys.argv[6]                 # XML_VerwachtingswaardePolderpeil wel of niet updaten
Skol        = "SORTEERVOLGORDE2"          # kolom met de sorteervolgorde van de punten.
Xkol        = "X_WAARDE"
Ykol        = "Y_WAARDE"
Zkol        = "Z_WAARDE"
BGkol       = "LENGTE_TOT_BG"             # lengte van alle punten tot het beginpunt v/h profiel
#---
# obv VakFC bepalen in welke *.gdb PWK_PROFIELBESTANDEN_def, PWK_GEO_PROFIELLIJNEN en PWK_DWARSPROFIEL_POINT staan.
lnPNTfc = arcpy.Describe(VakFC).path + "/PWK_PROFIELBESTANDEN_def"
lnFC = arcpy.Describe(VakFC).path + "/PWK_GEO_PROFIELLIJNEN"
PPfc = arcpy.Describe(VakFC).path + "/PWK_DWARSPROFIEL_POINT"
for fc in [lnPNTfc,lnFC,PPfc]:
    chk = arcpy.Exists(fc)
    if not chk:
        arcpy.AddError("FC: "+fc+" bestaat niet!!\nEINDE...")
        sys.exit()
#---
arcpy.env.overwriteOutput = True
arcpy.AddMessage("  >>> -------------------------------------")
arcpy.AddMessage("  >>> Snijpunt met profiel bepalen... ")
arcpy.AddMessage("  >>> -------------------------------------")
#---------------------------------------------------------
#---------------------------------------------------------
# ----  START
#---------------------------------------------------------
# Piping niet altijd 1 lijn dus alles samenvoegen tot 1 multipart
arcpy.Dissolve_management(pipFC, "in_memory/xxpipIN")
# Lijst maken met alle HRD punten om later te gebruiken en obv middelpunt te koppelen aan het vak
HRDpntLijst = []
HRDkolommen = ["OID@", "SHAPE@", HRDkol_org]
with arcpy.da.SearchCursor(HRDfc, HRDkolommen) as HRDcursor:
    for H in HRDcursor:
        HRDpntLijst.append([H[0],H[1],H[2]])
del H, HRDcursor
spatial_ref = arcpy.Describe(HRDfc).spatialReference
#---------------------------------------------------------
# 1 vak uitlezen en per vak naam prof vinden en verder verwerken
arcpy.AddMessage("-------------------------------------")
with arcpy.da.UpdateCursor(VakFC, VAKkols) as cursor:
  for row in cursor:    
    Rprof = row[0]
    AP = row[5]
    arcpy.AddMessage("Vak: "+str(row[2]))
    if Rprof:
        arcpy.AddMessage("  Representatief profiel: "+str(Rprof))    
        # 2 proflijn selecteren uit PWK_GEO_PROFIELLIJNEN dit zijn 2 stukken eerst samenvoegen.
        waar = LnmKol + " = '"+Rprof+"'"        
        with arcpy.da.SearchCursor(lnFC, ["SHAPE@", LnmKol, Tkol], where_clause=waar) as LNcursor:            
            for Lrow in LNcursor:
                if Lrow[2] == "Binnentalud":
                    Lbin = Lrow[0].lastPoint
                elif Lrow[2] == "Buitentalud":
                    Lbui = Lrow[0].lastPoint
            # De dwarsprofiel lijn
            # De eindpunten selecteren en dan de lijn opbouwen anders is de richting bui --> bin niet altijd juist.
            sr = arcpy.SpatialReference(28992)
            DeLijn = arcpy.Polyline(arcpy.Array([Lbui,Lbin]),sr)
        #---------------------------------------------------------
        # Nu naar de punten
        were = LnmKol + " = '"+Rprof+"'"
        Pkolommen = [Xkol, Ykol, Zkol, LnmKol, BGkol, Skol]
        afstandP = 0
        ProfPunt = 0
        # 1e punt uitlezen.
        sort = None,"ORDER BY "+Skol
        with arcpy.da.SearchCursor(PPfc, Pkolommen, where_clause=were, sql_clause=sort) as cursor2:
            row2 = cursor2.next()
            X = round(row2[0],4)
            Y = round(row2[1],4)
            Z = round(row2[2],3)
            arcpy.AddMessage("  XYZ: "+str(row2[5])+" - "+str(X)+"/"+str(Y)+"/"+str(Z))
            ProfPunt = arcpy.PointGeometry(arcpy.Point(X,Y))
        afstandP = DeLijn.measureOnLine(ProfPunt)
        arcpy.AddMessage("  Afstand 1e profielpunt tov begin dwarsprofiellijn: "+str(round(afstandP,2)))
        row[6] = round(afstandP,2)        
        #---------------------------------------------------------        
        # Nu snijpunt van de lijnen vinden
        afstand = 0
        afstandNEW = 0
        SnijPunt = 0
        GeenSpunt = 0
        with arcpy.da.SearchCursor("in_memory/xxpipIN", ["SHAPE@"]) as Pcursor:
          for pip in Pcursor:
            # eerst kijken of de lijnen elkaar wel snijden. Zo niet dan is True en kan er geen intersect gedaan worden.
            controle = pip[0].disjoint(DeLijn)
            if controle:
                arcpy.AddWarning("  Geen Snijpunt dan 1e profielpunt gebruiken.")
                # dan is het 1e punt van het profiel het in/uit trede punt
                SnijPunt = ProfPunt.firstPoint
            else:
                # het snijpunt bepalen en wegschrijven            
                PP = pip[0].intersect(DeLijn, 1)
                if PP.type != 'polyline':
                  for p in PP:
                    arcpy.AddMessage("  Snijpunt xy = "+str(p))
                    SnijPunt = p
            afstand = DeLijn.measureOnLine(SnijPunt)
            arcpy.AddMessage("  Afstand snijpunt tov begin profiel = "+str(round(afstand,2))+"m")
            # Als het surfaceprofiel(in de CSV) niet bij het begin v/d lijn begint dan afstand corrigeren met afstandP
            if afstandP > 0:
              arcpy.AddMessage("\n  In-/uittrede gecorrigeerd obv beginpunt profiel!")
              afstandNEW = afstand - afstandP                  
              # negatief mag niet in Ringtoets dus dan op 0 zetten.                  
              if afstandNEW < 0:                      
                  afstandNEW = 0
              row[1] = round(afstandNEW,2)
              if AP == None:
                  row[5] = "In-/uittrede gecorrigeerd obv beginpunt profiel!"
              else:
                  # kolom is max 200 karakters dus op 200 afkappen en dubbelingen eruit halen                          
                  AP = AP.replace("; In-/uittrede gecorrigeerd obv beginpunt profiel!","",10)
                  AP = AP.replace("In-/uittrede gecorrigeerd obv beginpunt profiel!","",10)
                  AP = AP+"; In-/uittrede gecorrigeerd obv beginpunt profiel!"
                  if len(AP) > 200:
                      arcpy.AddWarning("  Te veel tekst in de kolom Aandachtspunten, wordt afgekapt op 200 karakters")
                      AP = AP[:200]
                  row[5] = AP
              arcpy.AddMessage("  Bepaalde afstand:      "+str(round(afstand,2))+"\nGecorrigeerde afstand: "+str(round(afstandNEW,2)))
            else:
              row[1] = round(afstand,2)
        #----------------------------------------------------------
        # HRD zoeken
        # Nu een near tov de HRD locaties
        if HRD_jn == 'true':
            arcpy.AddMessage("-------------------------------------")
            naam = ''
            afst = 100000
            middenLijn = DeLijn.positionAlongLine(0.5, True)
            for hr in HRDpntLijst:
                dist = middenLijn.distanceTo(hr[1])
                if (dist < afst):
                    afst = dist
                    naam = hr[2]
            arcpy.AddMessage("HRD: "+naam+"  afstand: "+str(round(afst,2))+"m")
            row[3] = naam
        #----------------------------------------------------------
        # Als XML_VerwachtingswaardePolderpeil geupdate moet worden dan nog dichtsbijzijnde profielpunt zoeken en de Z overnemen.
        arcpy.AddMessage("-------------------------------------")
        if VW == 'true':
            arcpy.AddMessage("XML_VerwachtingswaardePolderpeil bepalen.")
            afst = 100000
            n = 0
            wrd = 0
            dist = 0
            # Alleen de punten selecteren die een Z hebben > -10 en
            waarP = LnmKol + " = '"+Rprof+"' AND Z_WAARDE > -10"
            n = len(list(i for i in arcpy.da.SearchCursor(lnPNTfc, ["SHAPE@",LnmKol,"X_WAARDE","Y_WAARDE","Z_WAARDE"], where_clause=waarP)))
            arcpy.AddMessage("  Er is/zijn: "+str(n)+" dwarsprofielpunten geselecteerd!")
            # Als er geen Snijpunt is dan kunnen we niet het dichtsbijzijnde punt selecteren dus gebruiken we het 1e punt op van de lijn.
            arcpy.AddMessage("  XY Snijpunt: "+str(SnijPunt.X)+" / "+str(SnijPunt.Y))
            # door de profielpunten loopen en de dichtsbijzijnde vinden.
            with arcpy.da.SearchCursor(lnPNTfc, ["SHAPE@",LnmKol,"X_WAARDE","Y_WAARDE","Z_WAARDE"], where_clause=waarP) as Pcursor:                
                for Prow in Pcursor:
                    X = Prow[2]
                    Y = Prow[3]
                    Z = Prow[4]
                    n = n + 1
                    PP = arcpy.PointGeometry(arcpy.Point(X,Y))
                    dist = arcpy.PointGeometry(SnijPunt).distanceTo(PP)
                    if (dist < afst):
                        afst = dist
                        wrd = Z
            arcpy.AddMessage("XML_VerwachtingswaardePolderpeil = "+str(round(wrd,2)) +"\n  afstand punt tov snijpunt: "+ str(round(afst,2)))
            row[4] = round(wrd,2)
        # het vak updaten.
        cursor.updateRow(row)
    else:
        arcpy.AddWarning("Vak heeft geen representatief profiel!")
    arcpy.AddMessage("-------------------------------------")
    arcpy.AddMessage("-------------------------------------")
#-----------------
arcpy.AddMessage("\n  >>>  KLAAR!  <<<")
