# -*- coding: cp1252 -*-
# --------------------------------------------------------------------------
# Witteveen+Bos
# ing. H.E.J. Nieuwland - augustus 2018
# --------------------------------------------------------------------------
# versie 1.0.0
# --------------------------------------------------------------------------
# PROFIELLIJN_MEDIAAN met geselecteerde profiellijnen. Van deze lijnen wordt de kolom RepresentatiefProfiel
# gevuld met: ‘Ja’
# --------------------------------------------------------------------------
import string, os, sys, locale, arcpy
# INPUT
Profl    = sys.argv[1]                 # MEDIAAN Layer met de geselecteerde dwarsprofiellijnen
PnmKol   = "PROFIELNAAM"               # kolom met profielnaam tbv def query
Kol      = "RepresentatiefProfiel"     # Representatief kolom
PkolVAK  = "REPROF_NAAM"               # kolom aan vakken bestand voor naam representatief profiel.
RemRP    = sys.argv[2]                 # Al bestaande profielen verwijderen?
#---
arcpy.env.overwriteOutput = True
arcpy.AddMessage("  >>> -------------------------------------")
arcpy.AddMessage("  >>> Representatief profiel selecteren... ")
arcpy.AddMessage("  >>> -------------------------------------")
#---------------------------------------------------------
#---------------------------------------------------------
# ----  START  ----
#---------------------------------------------------------
#n = len(list(i for i in arcpy.da.SearchCursor(Profl, [PnmKol, Kol])))
n = arcpy.Describe(Profl).fidset.split(';')
if n[0] == '':
    n = 0    # Bij geen selectie is n[0] '' en zet ik hier even op 0.
else:
    n = len(n)
arcpy.AddMessage("Er is/zijn: "+str(n)+" dwarsprofiel(en) geselecteerd!")
# controle op n selected
if n == 0:
    arcpy.AddError("Selecteer minimaal 1 dwarsprofiel!")
    sys.exit()
#--- Nu de profiel(en) verwerken
if n >= 1:    
    # Nu de layer zoeken om de definition query er op zetten.
    mxd = arcpy.mapping.MapDocument("CURRENT")
    Delyr = ''
    for lyr in arcpy.mapping.ListLayers(mxd):
        if lyr.longName == Profl:
            Delyr = lyr
    naamLijst = []
    with arcpy.da.SearchCursor(Profl, [PnmKol, Kol]) as cursor2:
        for row2 in cursor2:
            arcpy.AddMessage("Naam: "+str(row2[0]))
            naamLijst.append(row2[0])
    del row2, cursor2, mxd, lyr
    # Als er al eens een profiel is geselecteerd de kolom Kol leeg maken als optie is aangevinkt
    if RemRP == 'true':
        arcpy.AddMessage("oude representatieve profielen verwijderen...")
        arcpy.SelectLayerByAttribute_management(Delyr, "CLEAR_SELECTION")
        waar = Kol + " = 'Ja'"
        no = len(list(i for i in arcpy.da.SearchCursor(Profl, [PnmKol, Kol], where_clause=waar)))
        if no > 0:
            with arcpy.da.UpdateCursor(Profl, [PnmKol, Kol], where_clause=waar) as cursor3:
                for row3 in cursor3:
                    row3[1] = 'Nee'
                    cursor3.updateRow(row3)
            del row3, cursor3
    else:
        arcpy.AddMessage("oude representatieve profielen blijven behouden...")
        # Dus de naamlijst aanvullen met de al aanwezige repr. profielen.
        #arcpy.AddMessage("naamLijst:  "+str(naamLijst))
        arcpy.SelectLayerByAttribute_management(Delyr, selection_type="ADD_TO_SELECTION", where_clause="RepresentatiefProfiel = 'Representatief profiel'")
        with arcpy.da.SearchCursor(Profl, [PnmKol, Kol]) as cursor2:
            for row2 in cursor2:
                pnaam = str(row2[0])
                #arcpy.AddMessage("Naam: "+ pnaam)
                lst = set(naamLijst)
                if pnaam not in lst:
                    naamLijst.append(pnaam)
        arcpy.AddMessage("naamLijst:  "+str(naamLijst))
    # Nu de definition query er op zetten.
    nm = 0
    for naam in naamLijst:
        nm = nm + 1
        if nm == 1:
            defQ = PnmKol+" = '"+naam+"'"
        else:
            defQ = defQ + " OR "+PnmKol+" = '"+naam+"'"
    # Nu de definition query er op zetten.
    Delyr.definitionQuery = defQ
    # Nu is alleen het profiel geselecteerd en kan de kolom Kol gevuld worden.
    with arcpy.da.UpdateCursor(Profl, [PnmKol, Kol]) as cursor4:
        for row4 in cursor4:
            row4[1] = "Ja"
            cursor4.updateRow(row4)
        del row4, cursor4
    # Ook nog even de XY-as toevoegen
    Delyr.definitionQuery = Kol +" = 'Ja'"
    # selectie verwijderen.
    arcpy.SelectLayerByAttribute_management(Delyr, "CLEAR_SELECTION")
    arcpy.RefreshActiveView()
    #---------------------------------------------------------------------------------------------------------
arcpy.AddMessage("\n  >>>  KLAAR!  <<<")
