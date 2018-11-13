# --------------------------------------------------------------------------
# Wegschrijven vakken naar *.PRFL tbv HYDRA-NL
# Witteveen+Bos
# ing. H.E.J. Nieuwland - augustus 2018
# --------------------------------------------------------------------------
# versie 1.0.0
# --------------------------------------------------------------------------
# 22-08-2018 -  Maakt een directorie structuur aan per HRD punt en schrijft 
#               daar de prfl files in weg. Ook de Damwanden
# --------------------------------------------------------------------------
import string, os, sys, locale, arcpy
from time import strftime
tijd = strftime("%m-%d-%Y %H:%M:%S")

# INPUT
VakFC        = sys.argv[1]             # Lijnen FC met de vakken
IDkol        = "ID"                    # Kolom met id vak
Vkol         = "Vaknaam"               # Kolom met naam vak
odir         = sys.argv[2]             # uitvoer map
alles        = sys.argv[3]             # alleen de damwanden of alles
normaal      = "PRFL_DijkNormaal"      # de normaal tov noorden van de profiellijn kolom Normaal
ruwheid      = 1.0                     # de standaard ruwheid
ruw_kol1     = "Ruw_BuiTal_1"          # ruwheid vanaf de kruin naar volgende punt
ruw_kol2     = "Ruw_BuiTal_2"          # ruwheid 2e segment
ruw_kol3     = "Ruw_BuiTal_3"          # ruwheid 3e segment
ruw_kol4     = "Ruw_BuiTal_4"          # ruwheid 4e segment
ruw_kol5     = "Ruw_BuiTal_5"          # ruwheid 5e segment
kol          = "PRFLpunten"            # vaste kolom waar het type punt in staat
Opmkol       = "PRFL_Opmerkingen"      # de opmerkingen kolom
Khgt         = "PRFL_KruinHgt"         # de door de gebruiker bepaalde Kruinhoogte incl. eventuele zetting
Uitkol       = "UIT_PRFL_Bestand"      # kolom waar het volledig path naar de prfl in kan worden weggeschreven. max. 250 anders alleen de naam
Typekol      = "TypeDijk"              # type moet groene dijk zijn damwand wordt in een andere routine speciaal voor Hydra-NL geexporteerd.
HRDkol       = "HRD_Name"              # Naam van de dichtsbijzijnde HRD locatie
#--------------------------------------------------------------------------------------------------
# databasedir bepalen
workspace = arcpy.Describe(VakFC).path
arcpy.env.workspace = workspace
#---
arcpy.env.overwriteOutput = True
arcpy.AddMessage("\n  >>> ----------------------------------")
arcpy.AddMessage("  >>> Wegschrijven prfl ")
arcpy.AddMessage("  >>> ----------------------------------")
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
# ----  START  ----
#--------------------------------------------------------------------------------------------------
# per vak naam uitlezen, profielnamen selecteren en lijst van maken.
kolommen = ["OID@", "SHAPE@", IDkol, Vkol, Opmkol, ruw_kol1, ruw_kol2, ruw_kol3, ruw_kol4, ruw_kol5, normaal, Typekol, HRDkol, Khgt]
# Aantal vakken uitlezen.
# eerst kijken of we alleen de damwanden doen of alles.
if alles != "true":
  waar = Typekol +" = 'damwand'"
else:
  waar = Typekol +" <> 'alles'"
countTOT = len(list(i for i in arcpy.da.SearchCursor(VakFC, kolommen)))
count = len(list(i for i in arcpy.da.SearchCursor(VakFC, kolommen, where_clause=waar)))
arcpy.AddMessage("\nAantal vakken: "+str(count)+" van "+str(countTOT)+" verwerken.")
#-------------------------
vaknr = 0
with arcpy.da.SearchCursor(VakFC, kolommen, where_clause=waar, sql_clause=(None, 'ORDER BY '+HRDkol)) as cursor:
    for row in cursor:
        Pshp  = "PRFL_P_"+row[2].replace('-','_')
        FOUT1 = False   # als de benodigde variabelen niet juist zijn dan geen PRFL wegschrijven!
        vaknr = vaknr + 1
        VakID = str(row[2])
        Vnaam = row[3]
        #-- De PRFL punten FC selecteren en de punten uitlezen.
        Opm  = row[4]
        ruw1 = row[5]
        ruw2 = row[6]
        ruw3 = row[7]
        ruw4 = row[8]
        ruw5 = row[9]
        NORMAAL = row[10]
        ProfType = row[11]        
        hrd = row[12]
        Zkrn = row[13]
        arcpy.AddMessage("\n--------------------------------")
        arcpy.AddMessage("VakID:        "+str(VakID))
        arcpy.AddMessage("Naam:         "+str(Vnaam))
        arcpy.AddMessage("Type dijk:    "+str(ProfType))
        arcpy.AddMessage("HRD locatie:  "+str(hrd)+"\n")
        kolommen = ["SHAPE@XY", kol]
        were = kol +" LIKE '%_prfl'"
        #---------------------------------------------------------
        # check of de waarden van de uitgelezen kolommen(van het VAK) bruikbaar zijn.
        # dus ruw1-ruw5 moeten er zijn als er ook meerdere taludsegmenten zijn.
        # Dit is in de voorgaande stappen gecontroleerd dus wordt er hier vanuit gegaan dat de waarden juist zijn.
        if ProfType == "groene dijk":
          if ruw1 >= 0.5 and ruw1 <= 1.0:
              arcpy.AddMessage("ruw1 = ok")
          else:
              arcpy.AddWarning("ruw1 = "+str(ruw1)+" = Niet ingevoerd! wordt op 1 gezet!")
              ruw1 = ruwheid
          if ruw2 >= 0.5 and ruw1 <= 1.0:
              arcpy.AddMessage("ruw2 = ok")
          else:
              arcpy.AddWarning("ruw2 = "+str(ruw2)+" = Niet ingevoerd! wordt op 1 gezet")
              ruw2 = ruwheid
          if ruw3 >= 0.5 and ruw1 <= 1.0:
              arcpy.AddMessage("ruw3 = ok")
          else:
              arcpy.AddWarning("ruw3 = "+str(ruw3)+" = Niet ingevoerd! wordt op 1 gezet")
              ruw3 = ruwheid
          if ruw4 >= 0.5 and ruw1 <= 1.0:
              arcpy.AddMessage("ruw4 = ok")
          else:
              arcpy.AddWarning("ruw4 = "+str(ruw4)+" = Niet ingevoerd! wordt op 1 gezet")
              ruw4 = ruwheid
          if ruw5 >= 0.5 and ruw1 <= 1.0:
              arcpy.AddMessage("ruw5 = ok")
          else:
              arcpy.AddWarning("ruw5 = "+str(ruw5)+" = Niet ingevoerd! wordt op 1 gezet")
              ruw5 = ruwheid
        # deze moet er altijd zijn
        if NORMAAL > 0 and NORMAAL < 401:
            arcpy.AddMessage("Normaal = ok")
        else:
            arcpy.AddError("Normaal = "+str(NORMAAL)+" = Niet juist!")
            FOUT1 = True
        #---------------------------------------------------------
        # Als de FC er niet is dan vak overslaan.
        Pchk = arcpy.Exists(Pshp)
        #---------------------------------------------------------
        if Pchk and FOUT1 == False:
            # uitlezen PRFL punten FC.
            count = len(list(i for i in arcpy.da.SearchCursor(Pshp, kolommen, where_clause=were)))
            arcpy.AddMessage("Aantal punten: "+str(count))
            XYlijst  = []
            VOORLlst = []
            TALUDlst = []
            # -------------------------
            if count > 0:
                # folder structuur aanmaken
                # als hrd map niet bestaat dan aanmaken incl. Profielen map.
                uitmap = odir+"/"+hrd
                HRDchk = arcpy.Exists(hrd)
                if not HRDchk:
                  try:
                    arcpy.CreateFolder_management(odir, hrd)
                  except:
                    print ""
                  try:
                    arcpy.CreateFolder_management(uitmap, "Profielen")
                  except:
                    print ""
                with arcpy.da.SearchCursor(Pshp, kolommen, where_clause=were) as cursor:
                    for row in cursor:
                        xy = row[0]
                        XYlijst.append(xy)
                        Pnm = row[1]
                        #arcpy.AddMessage(Pnm)
                        # Voorland (kunnen meerdere punten zijn
                        if Pnm == 'Voorland_prfl':
                            VOORLlst.append(xy)
                        # Buitenteen (altijd 1)
                        elif Pnm == 'Buitenteen_prfl':
                            TEEN = xy
                        elif Pnm == "Damwand_prfl":
                            DAMW = xy
                        # Kruin (altijd 1)
                        elif Pnm == 'Buitenkruin_prfl':
                            KRUIN = xy
                        elif Pnm == 'Taludknik_prfl':
                            TALUDlst.append(xy)
                VOORLlst = sorted(VOORLlst)
                TALUDlst = sorted(TALUDlst)
                # recht talud anders behandelen als een getrapt talud.
                # alleen bij groene dijk
                if ProfType == "groene dijk":
                  if len(TALUDlst) == 0 and ProfType == "groene dijk":
                      # Maar 2 punten en dat zijn de teen en kruin
                      TALUDlst.append([TEEN[0],TEEN[1],ruw1])
                      TALUDlst.append([KRUIN[0],KRUIN[1],ruw1])
                  elif len(TALUDlst) < 5:
                      # meerdere taludpunten
                      # altijd de kruin, teen en 1 of meer taludknikpunten                
                      TALUDlst.append(TEEN)
                      TALUDlst = sorted(TALUDlst)
                      tmpLST = []
                      nr = len(TALUDlst)
                      for PNT in TALUDlst:
                          # punt toevoegen incl. juiste ruwheid
                          tmpLST.append([PNT[0],PNT[1],eval("ruw"+str(nr))])
                          nr -= 1                
                      tmpLST.append([KRUIN[0],KRUIN[1],ruw1])   # ruwheid is altijd de 1e maar doet er niet toe voor Ringtoets.
                      TALUDlst = sorted(tmpLST)
                  else:
                      arcpy.AddError(" Er zijn meer dan 5 taludknikpunten! Verwijder of voeg punt(en) toe!")
                      FOUT1 = True
                #-----
                if FOUT1 == False:    
                    XYlijst = sorted(XYlijst)
                    #---                    
                    # X0 bepalen = begin profiel tot referentielijn(X=0)
                    X0 = int(XYlijst[0][0])
                    oprfl_naam = "PRFL_"+Vnaam+".prfl"
                    uitdir = uitmap+"/Profielen"
                    # Ook de uitvoer prfl bestandsnaam en path wegschrijven. Indien > 250 kar dan alleen bestandsnaam
                    # Alleen voor de damwand prfl's de groene dijken moeten naar de Ringtoetsmap verwijzen.
                    if ProfType == "damwand":
                      were = IDkol+" = '"+VakID+"'"
                      kolommen = [IDkol,Uitkol,"X0"]
                      BestNaam = os.path.join(uitdir,oprfl_naam)
                      if len(BestNaam) > 250:
                        BestNaam = oprfl_naam
                      with arcpy.da.UpdateCursor(VakFC, kolommen, where_clause=were) as Updcursor:
                        for row in Updcursor:
                          row[1] = BestNaam
                          row[2] = X0
                          # het vak updaten.
                          Updcursor.updateRow(row)
                    # Nu *prfl maken
                    
                    # uitvoer txt file killen als ie al bestaat.
                    try:
                        arcpy.Delete_management(uitdir+"/"+oprfl_naam, "File")
                    except:
                        print("")
                    # Open prfl file
                    ll = open(uitdir+"/"+oprfl_naam, "w")
                    ll.write("VERSIE\t4.0\n")
                    ll.write("\n")
                    ll.write("ID\t" + str(VakID) + "\n")
                    ll.write("\n")
                    ll.write("RICHTING\t" + str(round(NORMAAL,2)) + "\n")
                    ll.write("\n")
                    ll.write("DAM\t0\n")
                    ll.write("\n")
                    ll.write("DAMHOOGTE\t0\n")
                    ll.write("\n")
                    Nv = len(VOORLlst) + 1
                    ll.write("VOORLAND\t" + str(Nv) + "\n")
                    for pp in VOORLlst:             
                        ll.write(str('{:,.3f}'.format(pp[0])) +"\t" + str('{:,.3f}'.format(pp[1])) + "\t"+ str(ruwheid) + "\n")
                    # Als laatste voorland op de teen of damwand aan laten sluiten
                    if ProfType == "groene dijk":
                      ll.write(str('{:,.3f}'.format(TEEN[0])) +"\t"+ str('{:,.3f}'.format(TEEN[1])) +"\t"+ str(ruwheid) + "\n")
                    elif ProfType == "damwand":
                      ll.write(str('{:,.3f}'.format(DAMW[0])) +"\t"+ str('{:,.3f}'.format(DAMW[1])) +"\t"+ str(ruwheid) + "\n")
                    ll.write("\n")
                    if ProfType == "damwand":
                      ll.write("DAMWAND\t1\n")              # WRIJ=altijd damwand zonder neusconstructie = 1
                    elif ProfType == "groene dijk":
                      ll.write("DAMWAND\t0\n")
                    ll.write("\n")
                    ll.write("KRUINHOOGTE\t" + str(round(Zkrn,2)) + "\n")
                    ll.write("\n")
                    if ProfType == "damwand":
                      ll.write("DIJK\t"+str(0)+"\n")
                    elif ProfType == "groene dijk":
                      Kv = len(TALUDlst)
                      ll.write("DIJK\t"+str(Kv)+"\n")
                      for KRNpnt in TALUDlst:
                        ll.write(str('{:,.3f}'.format(KRNpnt[0])) +"\t"+ str('{:,.3f}'.format(KRNpnt[1])) +"\t"+ str('{:,.3f}'.format(KRNpnt[2])) + "\n")
                    ll.write("\n")
                    ll.write("MEMO\n")
                    ll.write("\nWaterschap Rijn en IJssel\n\n")
                    ll.write("Profiel gegenereed op:\t")
                    ll.write("'" + str(tijd) + "'\n")
                    ll.write("Vaknaam:\t\t")
                    ll.write(str(Vnaam)+"\n")            
                    ll.write("Opmerkingen:\t\t")
                    ll.write(str(Opm)+"\n")
                    ll.flush()
                    ll.close()
                    #----
                    arcpy.AddMessage("\n--  Resultaten weggeschreven naar:  \n--  " + oprfl_naam + "\n" + "--  In de folder:\n--  "+str(uitdir)+"\n")
            else:
                arcpy.AddError("geen prfl punten!!")
del row, cursor
#-------------------------------------------------------------------------------------------------------------------------
arcpy.AddMessage("--------------------------------")
arcpy.AddMessage("\n  >>>  KLAAR!  <<<\n")
arcpy.AddMessage("--------------------------------")
arcpy.AddMessage("  Open nu HYDRA-NL kies een werkmap en laad de bijbehorende hydraulische database in.")
arcpy.AddMessage("  Sluit HYDRA-NL en kopieer de net aangemaakte mappen in de map met de naam van de HR database.\n  Als je nu HYDRA-NL opent moet je de profielen zien.")
arcpy.AddMessage("--------------------------------\n")
