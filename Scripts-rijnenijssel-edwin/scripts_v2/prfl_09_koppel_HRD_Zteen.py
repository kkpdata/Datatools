# --------------------------------------------------------------------------
# Witteveen+Bos
# ing. H.E.J. Nieuwland - augustus 2018
# --------------------------------------------------------------------------
# versie 1.0.0
# --------------------------------------------------------------------------
# 28-08-2018 -  Koppel HRD resultaten(4 kolommen) aan het vak obv gekozen HRD locatie.
#               En koppel Z teen punt uit prfl aan vak. kolom = PRFL_Zteen
# --------------------------------------------------------------------------
import string, os, sys, locale, arcpy

# INPUT
VakFC        = sys.argv[1]             # Lijnen FC met de vakken
IDkol        = "ID"                    # Kolom met id vak
Vkol         = "Vaknaam"               # Kolom met naam vak
HRDkol       = "HRD_Name"              # Naam van de dichtsbijzijnde HRD locatie
HRDfc        = sys.argv[2]             # HRD FC
Nkol         = "Name"                  # naam van het HRD punt
HRDkols      = ["Signaleringswaarde_Waterstand","Signaleringswaarde_Golfhoogte","Ondergrens_Waterstand","Ondergrens_Golfhoogte"]  # de 4 HRD resultaat kolommen
kol          = "PRFLpunten"            # vaste kolom waar het type punt in staat
Zkol         = "PRFL_Zteen"            # Z waarde van teenpunt uit PRFL file/FC
# --------------------------------------------------------------------------------------------------
# databasedir bepalen
workspace = arcpy.Describe(VakFC).path
arcpy.env.workspace = workspace
#---
arcpy.env.overwriteOutput = True
arcpy.AddMessage("\n  >>> ----------------------------------")
arcpy.AddMessage("  >>> Koppelen HRD en Zteen ")
arcpy.AddMessage("  >>> ----------------------------------")
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
# ----  START  ----
#--------------------------------------------------------------------------------------------------
# Kolommen aan vak toevoegen indien nog niet aanwezig.
KOLlijst = HRDkols[:]    # kopie maken van de lijst
KOLlijst.append(Zkol)
for KK in KOLlijst:
  try:
    arcpy.AddMessage("Kolom "+KK+" toevoegen...")
    arcpy.AddField_management(VakFC, KK, "DOUBLE")
  except:
    arcpy.AddError("Kolom "+KK+" bestaat al! Controleer zelf of type en length juist zijn.")
# per vak naam uitlezen, profielnamen selecteren en lijst van maken.
kolommen = [IDkol, Vkol, HRDkol]
kolommen.extend(KOLlijst)
# Aantal vakken uitlezen.
countTOT = len(list(i for i in arcpy.da.SearchCursor(VakFC, kolommen)))
arcpy.AddMessage("\nAantal vakken: "+str(countTOT))
#-------------------------
with arcpy.da.UpdateCursor(VakFC, kolommen, sql_clause=(None, 'ORDER BY '+Vkol)) as cursor:
    for row in cursor:
        Pshp  = "PRFL_P_"+row[0].replace('-','_')
        VakID = str(row[0])
        Vnaam = row[1]
        HRD   = row[2]
        arcpy.AddMessage("\n--------------------------------")
        arcpy.AddMessage("VakID:        "+str(VakID))
        arcpy.AddMessage("Naam:         "+str(Vnaam))
        arcpy.AddMessage("HRD locatie:  "+str(HRD))
        #---------------------------------------------------------
        # HRD punten en PRFL_P_ punten van het vak uitlezen
        #---------------------------------------------------------
        HRDcount = len(list(i for i in arcpy.da.SearchCursor(HRDfc, Nkol)))
        arcpy.AddMessage("HRDcount:  "+str(HRDcount)+"\n")        
        if HRDcount > 0 and HRD != None:
          were = Nkol +" = '"+HRD+"'"
          Hkolommen = HRDkols[:]   # kopie maken van de lijst
          Hkolommen.append(Nkol)
          with arcpy.da.SearchCursor(HRDfc, Hkolommen, where_clause=were) as Hcursor:
            for Hrow in Hcursor:
              Nm = Hrow[4]
              SW = Hrow[0]
              SG = Hrow[1]
              OW = Hrow[2]
              OG = Hrow[3]
              arcpy.AddMessage("Nm:      "+str(Nm))
              arcpy.AddMessage("SW:      "+str(SW))
              arcpy.AddMessage("SG:      "+str(SG))
              arcpy.AddMessage("OW:      "+str(OW))
              arcpy.AddMessage("OG:      "+str(OG))
              row[3] = Hrow[0]
              row[4] = Hrow[1]
              row[5] = Hrow[2]
              row[6] = Hrow[3]
        else:
          arcpy.AddWarning("Geen HRD locatie ingevuld of naam niet gevonden!!")
        #---------------------------------------------------------
        # PRFL punten teen uitlezen
        #---------------------------------------------------------
        # Als de FC er niet is dan vak overslaan.
        Pchk = arcpy.Exists(Pshp)
        Pkolommen = ["SHAPE@XY", kol]
        were = kol +" = 'Buitenteen_prfl'"
        #---------------------------------------------------------
        if Pchk:
            # uitlezen PRFL punten FC.
            with arcpy.da.SearchCursor(Pshp, Pkolommen, where_clause=were) as Pcursor:
              for Prow in Pcursor:
                Z = Prow[0][1]
                arcpy.AddMessage("Zteen:   "+str(round(Z,2)))
                row[7] = Prow[0][1]
        else:
          arcpy.AddWarning("Geen PRFL punten met een buitenteen gevonden!!")
        #---------------------------------------------------------
        cursor.updateRow(row)
#-------------------------------------------------------------------------------------------------------------------------
arcpy.AddMessage("--------------------------------")
arcpy.AddMessage("\n  >>>  KLAAR!  <<<\n")
arcpy.AddMessage("--------------------------------")
arcpy.AddMessage("--------------------------------\n")
