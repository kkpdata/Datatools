# --------------------------------------------------------------------------
# GEKB berekenings resultaten uitlezen en koppelen
# ing. H.E.J. Nieuwland - augustus 2018
# --------------------------------------------------------------------------
# versie 1.0.1
# --------------------------------------------------------------------------
# De rtd uitlezen en koppelen naar csv en eventueel naar GDB table
# 20180911  -   Output naar CSV aangepast ivm landinstellingen probleem. ; als lijstschijdingsteken en , als decimaal symbool.
#               en kolomnamen gewijzigd.
# --------------------------------------------------------------------------
import string, os, sys, arcpy, time
# INPUT
inSQLite = sys.argv[1]    # SQLite Ringtoets project met de resultaten
HfdVar   = sys.argv[2]    # welk type RTD gaan we nu inlezen? 
Var      = sys.argv[3]    # welk type RTD gaan we nu inlezen? ivm kolomnamen en te runnen routine
Uitdir   = sys.argv[4]    # Uitvoer directory voor de CSV en GDB
naarGDB  = sys.argv[5]    # wel of niet naar gdb wegschrijven.
#---
if HfdVar == 'signaleringswaarde':      # obv welke grens is RTD gerekend.
    V1 = 'Sign'
elif HfdVar == 'ondergrens':
    V1 = 'Ondg'

if Var == 'golfhoogte':        # bij golfhoogte aparte berekening rest is standaard
    var = 2
    V2 = 'Golf'
elif Var == 'standaard':
    var = 1
    V2 = 'Basis'
elif Var == 'open_grasmat':
    var = 1
    V2 = Var
elif Var == 'golfh_klasse1_2':
    var = 1
    V2 = Var
elif Var == 'gevoeligheid3':
    var = 1
    V2 = 'Gev3'
elif Var == 'gevoeligheid4':
    var = 1
    V2 = 'Gev4'    
elif Var == 'gevoeligheid5':
    var = 1
    V2 = 'Gev5'

Hv = V1+"_"+V2

Var = Var.replace(" ","")
if naarGDB == 'true':
    naarGDB = True
else:
    naarGDB = False

arcpy.env.overwriteOutput = True
arcpy.AddMessage("  >>> ----------------------------------")
arcpy.AddMessage("  >>> SQLite met GEKB resultaten koppelen en wegschrijven naar csv. ")
arcpy.AddMessage("  >>> ----------------------------------")
uniek = time.strftime('%Y%m%d%H%M%S')
#---------------------------------------------------------
#---------------------------------------------------------
# ----  START ----
#---------------------------------------------------------
#---------------------------------------------------------
if var == 1:
    arcpy.AddMessage("  >>> ----------------------------------")
    arcpy.AddMessage("  >>> GEKB standaard resultaten uitlezen. ")
    arcpy.AddMessage("  >>> ----------------------------------")
    # Uit te lezen tabellen en structuur uitleg:
    # We gaan uit een Ringtoets project de GEKB resultaattabellen uitlezen en koppelen tot 1 totaal csv
    # 
    # GrassCoverErosionInwardsCalculationEntity
    # GrassCoverErosionInwardsDikeHeightOutputEntity
    # GrassCoverErosionInwardsOutputEntity
    # GrassCoverErosionInwardsOvertoppingRateOutputEntity
    # GrassCoverErosionInwardsSectionResultEntity
    # FailureMechanismSectionEntity
    # 
    # 1 = Toets niet uitgevoerd
    # 2 = Voldoende / Niet relevant
    # 3 = Nog geen oordeel
    # 
    if naarGDB:
        # eerst een lege gdb maken waar de dummy GIS tabellen in aanmaken.
        ogdb = Uitdir+"/GEKB_results.gdb"
        if not arcpy.Exists(ogdb):
            arcpy.AddMessage("Aanmaken lege GDB")
            arcpy.CreateFileGDB_management(out_folder_path=Uitdir, out_name="GEKB_results", out_version="CURRENT")
        else:
            arcpy.AddMessage("GDB bestaat al")
        # een lege tabel maken.
        tabnaam = "GEKB_"+Hv+"_CalculationResults_"+str(Var)+"_"+str(uniek)
        arcpy.AddMessage("Aanmaken lege tabel: "+tabnaam)
        arcpy.CreateTable_management(out_path=ogdb, out_name=tabnaam)
        Otab = ogdb+"/"+tabnaam
        # Kolommen toevoegen.
        arcpy.AddMessage("Kolommen toevoegen...")
        #arcpy.AddField_management(Otab, "SectionEntityId", "LONG", "4")
        arcpy.AddField_management(Otab, "Vaknaam", "TEXT", "", "", 100)
        #arcpy.AddField_management(Otab, Hv+"_CalculationEntityId", "LONG", "4")
        arcpy.AddField_management(Otab, "Faalkans_"+Hv, "TEXT", "", "", 20)
        if V2 == 'Basis':
            arcpy.AddField_management(Otab, "Overslag_dominant_"+Hv, "TEXT", "", "", 6)
        arcpy.AddField_management(Otab, "HBN_dsn_"+Hv, "DOUBLE")
        if V2 == 'Basis':
            arcpy.AddField_management(Otab, "HBN_Convergentie_"+Hv, "TEXT", "", "", 4)
            arcpy.AddField_management(Otab, "Overslag_norm_"+Hv, "DOUBLE")
            arcpy.AddField_management(Otab, "Overslag_norm_convergentie_"+Hv, "TEXT", "", "", 4)
            arcpy.AddField_management(Otab, "Faalkans_Toetslaag1_"+Hv, "TEXT", "", "", 30)
            arcpy.AddField_management(Otab, "Faalkans_Toetslaag2_"+Hv, "TEXT", "", "", 30)
            arcpy.AddField_management(Otab, "Faalkans_Toetslaag3_"+Hv, "DOUBLE")
    # CSV aanmaken en openen
    oCSV = Uitdir+"/GEKB_"+Hv+"_resultaten_"+str(Var)+"_"+uniek+".csv"
    ll = open(oCSV, "w")
    #---------------------------------------------------------
    # De kolomnamen uit de SQLite die uitgelezen worden
    KOLlijst1 = "FailureMechanismSectionEntityId, GrassCoverErosionInwardsCalculationEntityId, LayerOne, LayerThree"   # results
    KOLlijst2 = "FailureMechanismSectionEntityId, Name"       # Failure section
    KOLlijst3 = "GrassCoverErosionInwardsOutputEntityId, GrassCoverErosionInwardsCalculationEntityId, IsOvertoppingDominant, Probability"    # Sterkte
    KOLlijst4 = "GrassCoverErosionInwardsOutputEntityId, OvertoppingRate, CalculationConvergence"    # Overslag
    KOLlijst5 = "GrassCoverErosionInwardsOutputEntityId, DikeHeight, CalculationConvergence"    # HBN
    arcpy.AddMessage("SQLite openen en uitlezen...")
    # Nu de SQLite openen en uitlezen.
    import sqlite3
    conn = sqlite3.connect(inSQLite)
    cursor = conn.cursor()
    #------------------
    if naarGDB:
        # cursor openen
        # De kolommen van de GIS table        
        if V2 == 'Basis':
            INkols = ["Vaknaam", "Faalkans_"+Hv, "Overslag_dominant_"+Hv, "HBN_dsn_"+Hv, "HBN_Convergentie_"+Hv, "Overslag_norm_"+Hv, "Overslag_norm_convergentie_"+Hv, "Faalkans_Toetslaag1_"+Hv, "Faalkans_Toetslaag2_"+Hv, "Faalkans_Toetslaag3_"+Hv]
        else:
            INkols = ["Vaknaam", "Faalkans_"+Hv, "HBN_dsn_"+Hv]
        insert_cursor = arcpy.da.InsertCursor(Otab,INkols)
    # INkols als 1e regel in de CSV
    if V2 == 'Basis':
        ll.write("Vaknaam;Faalkans_"+Hv+";Overslag_dominant_"+Hv+";HBN_dsn_"+Hv+";HBN_Convergentie_"+Hv+";Overslag_norm_"+Hv+";Overslag_norm_convergentie_"+Hv+";Faalkans_Toetslaag1_"+Hv+";Faalkans_Toetslaag2_"+Hv+";Faalkans_Toetslaag3_"+Hv+"\n")
    else:
        ll.write("Vaknaam;Faalkans_"+Hv+";HBN_dsn_"+Hv+"\n")
    #------------------
    # GrassCoverErosionInwardsSectionResultEntity
    cursor.execute("SELECT "+KOLlijst1+" FROM GrassCoverErosionInwardsSectionResultEntity ORDER BY FailureMechanismSectionEntityId DESC")
    for row0 in cursor.fetchall():
        kans = 'None'
        vaknr = row0[0]
        calcnr = row0[1]
        arcpy.AddMessage("Vaknr:  "+str(vaknr))
        arcpy.AddMessage("Berekeningnr:  "+str(calcnr))
        record = []
        #record.append(vaknr)
        #------------------
        # FailureMechanismSectionEntity uitlezen voor de vaknaam
        cursor.execute("SELECT "+KOLlijst2+" FROM FailureMechanismSectionEntity WHERE FailureMechanismSectionEntityId = "+str(vaknr))
        Rij1 = cursor.fetchall()
        ln1 = len(Rij1)
        if ln1 == 1:        
            for row1 in Rij1:
                record.append(row1[1])
            del row1
        else:
            arcpy.AddWarning("Tabel FailureMechanismSectionEntity bevat geen record voor FailureMechanismSectionEntityId: "+str(nr)+"!\nwaarden op 0")
            record.append(0)
        #------------------
        # Als berekening er is dan verder uitlezen anders alles op 0
        if calcnr != None:
            # STERKTE - GrassCoverErosionInwardsOutputEntity uitlezen
            cursor.execute("SELECT "+KOLlijst3+" FROM GrassCoverErosionInwardsOutputEntity WHERE GrassCoverErosionInwardsCalculationEntityId = "+str(calcnr))
            Rij2 = cursor.fetchall()
            ln2 = len(Rij2)
            # als er een record is dan toevoegen anders x aantal lege waarden toevoegen
            if ln2 == 1:
                for row2 in Rij2:
                    kans = "1/"+str(int(1 / row2[3]))
                    record.append(kans)
                    if V2 == 'Basis':
                        if row2[2] == 0:
                            record.append('False')
                        elif row2[2] == 1:
                            record.append('True')
                del row2
            else:
                arcpy.AddWarning("Tabel GrassCoverErosionInwardsOutputEntity bevat geen record voor GrassCoverErosionInwardsOutputEntityId: "+str(calcnr)+"!\nwaarden op 0")
                record.append('None')
                if V2 == 'Basis':
                    record.append('None')
            #------------------
            # HBN - GrassCoverErosionInwardsDikeHeightOutputEntity uitlezen    
            cursor.execute("SELECT "+KOLlijst5+" FROM GrassCoverErosionInwardsDikeHeightOutputEntity WHERE GrassCoverErosionInwardsOutputEntityId = "+str(calcnr))
            Rij3 = cursor.fetchall()
            ln3 = len(Rij3)
            # als er een record is dan toevoegen anders x aantal lege waarden toevoegen
            if ln3 == 1:
                for row3 in Rij3:
                    record.append(row3[1])
                    if V2 == 'Basis':
                        if row3[2] == 3:                  # ik weet zeker dat 3 Ja is andere waarden nog niet tegen gekomen.
                            record.append('Ja')
                        else:
                            record.append(row3[2])
                del row3
            else:
                arcpy.AddWarning("Tabel GrassCoverErosionInwardsDikeHeightOutputEntity bevat geen record voor GrassCoverErosionInwardsOutputEntityId: "+str(calcnr)+"!\nwaarden op 0")
                record.append(-9999)
                if V2 == 'Basis':
                    record.append('None')
            #------------------
            if V2 == 'Basis':
                # OVERSLAG - GrassCoverErosionInwardsDikeHeightOutputEntity uitlezen    
                cursor.execute("SELECT "+KOLlijst4+" FROM GrassCoverErosionInwardsOvertoppingRateOutputEntity WHERE GrassCoverErosionInwardsOutputEntityId = "+str(calcnr))
                Rij4 = cursor.fetchall()
                ln4 = len(Rij4)
                # als er een record is dan toevoegen anders x aantal lege waarden toevoegen
                if ln4 == 1:
                    for row4 in Rij4:
                        record.append(row4[1] * 1000)
                        if row4[2] == 3:
                            record.append('Ja')
                        else:
                            record.append(row4[2])
                    del row4
                else:
                    arcpy.AddWarning("Tabel GrassCoverErosionInwardsOvertoppingRateOutputEntity bevat geen record voor GrassCoverErosionInwardsOutputEntityId: "+str(calcnr)+"!\nwaarden op 0")
                    record.append(-9999)
                    record.append('None')
        #------------------
        else:
            if V2 == 'Basis':
                #record.append(calcnr)
                record.append('None')
                record.append('None')
                record.append(-9999)
                record.append('None')
                record.append(-9999)
                record.append('None')
            else:
                record.append('None')
                record.append(-9999)
        if V2 == 'Basis':
            #-- als laatste de toetslaag wegschrijven.
            wrd = ''
            if row0[2] == 1:
                wrd = 'Toets niet uitgevoerd'
            elif row0[2] == 2:
                wrd = 'Voldoende / Niet relevant'
            elif row0[2] == 3:
                wrd = 'Nog geen oordeel'
            record.append(wrd)   # = opzoeken 123
            record.append(kans)
            record.append(row0[3])
        #-- wegschrijven
        arcpy.AddMessage("Result: "+str(record))
        if naarGDB:
            insert_cursor.insertRow(record)
        v = ";".join(str(e).replace('.',',') for e in record)
        ll.write(v+"\n")
        #------------------
    del row0
    cursor.close()
    ll.close()
    try:
        del insert_cursor
    except:
        print ""
    #------------------
elif var == 2:
    arcpy.AddMessage("  >>> ----------------------------------")
    arcpy.AddMessage("  >>> GEKB golfoverslag resultaten uitlezen. ")
    arcpy.AddMessage("  >>> ----------------------------------")
    # Uit te lezen tabellen en structuur uitleg:
    # We gaan uit een Ringtoets project de GEKB resultaattabellen uitlezen en koppelen tot 1 totaal csv
    #
    # FailureMechanismSectionEntity
    # GrassCoverErosionInwardsSectionResultEntity
    # GrassCoverErosionInwardsDikeHeightOutputEntity
    # GeneralResultFaultTreeIllustrationPointEntity
    # TopLevelFaultTreeIllustrationPointEntity
    # FaultTreeSubmechanismIllustrationPointEntity
    # SubMechanismIllustrationPointEntity
    # IllustrationPointResultEntity
    # 
    if naarGDB:
        # eerst een lege gdb maken waar de dummy GIS tabellen in aanmaken.
        ogdb = Uitdir+"/GEKB_results.gdb"
        if not arcpy.Exists(ogdb):
            arcpy.AddMessage("Aanmaken lege GDB")
            arcpy.CreateFileGDB_management(out_folder_path=Uitdir, out_name="GEKB_results", out_version="CURRENT")
        else:
            arcpy.AddMessage("GDB bestaat al")
        # een lege tabel maken.
        tabnaam = "GEKB_"+Hv+"_CalculationResults_"+str(Var)+"_"+str(uniek)
        arcpy.AddMessage("Aanmaken lege tabel: "+tabnaam)
        arcpy.CreateTable_management(out_path=ogdb, out_name=tabnaam)
        Otab = ogdb+"/"+tabnaam
        # Kolommen toevoegen.
        arcpy.AddMessage("Kolommen toevoegen...")
        #arcpy.AddField_management(Otab, "SectionEntityId", "LONG", "4")
        arcpy.AddField_management(Otab, "Vaknaam", "TEXT", "", "", 100)
        #arcpy.AddField_management(Otab, Hv+"_CalculationEntityId", "LONG", "4")
        arcpy.AddField_management(Otab, "HBN_dsn_01lsm_"+V1, "DOUBLE")
        arcpy.AddField_management(Otab, "HBN_dsn_01lsm_Maatgevende_windr_"+V1, "TEXT", "", "", 4)
        arcpy.AddField_management(Otab, "Hs_bij_HBN_dsn_01lsm_"+V1, "DOUBLE")
    # CSV aanmaken en openen
    oCSV = Uitdir+"/GEKB_"+Hv+"_resultaten_"+str(Var)+"_"+uniek+".csv"
    ll = open(oCSV, "w")
    #---------------------------------------------------------
    # De kolomnamen uit de SQLite die uitgelezen worden    
    KOLlijst1 = "FailureMechanismSectionEntityId, GrassCoverErosionInwardsCalculationEntityId, LayerOne, LayerThree"   # results
    KOLlijst2 = "FailureMechanismSectionEntityId, Name"       # Failure section
    KOLlijst3 = "GrassCoverErosionInwardsOutputEntityId, GeneralResultFaultTreeIllustrationPointEntityId, DikeHeight"    # HBN
    KOLlijst4 = "GeneralResultFaultTreeIllustrationPointEntityId, GoverningWindDirectionName"  # GeneralResultFaultTreeIllustrationPointEntity
    KOLlijst5 = "FaultTreeIllustrationPointEntityId, GeneralResultFaultTreeIllustrationPointEntityId, WindDirectionName"  # TopLevelFaultTreeIllustrationPointEntity
    KOLlijst6 = "SubMechanismIllustrationPointEntityId, FaultTreeIllustrationPointEntityId"  # FaultTreeSubmechanismIllustrationPointEntity
    KOLlijst7 = "SubMechanismIllustrationPointEntityId, Name"  # SubMechanismIllustrationPointEntity
    KOLlijst8 = "SubMechanismIllustrationPointEntityId, Description, Value"  # IllustrationPointResultEntity
    arcpy.AddMessage("SQLite openen en uitlezen...")
    # Nu de SQLite openen en uitlezen.
    import sqlite3
    conn = sqlite3.connect(inSQLite)
    cursor = conn.cursor()
    #------------------
    if naarGDB:
        # cursor openen
        # De kolommen van de GIS table
        #INkols = ["SectionEntityId", "Vaknaam", Hv+"_CalculationEntityId", "HBN_"+Hv+"_Hoogte", "HBN_"+Hv+"_Maatgevende_windrichting", "HBN_"+Hv+"_Golfhoogte_Hs"]
        INkols = ["Vaknaam", "HBN_dsn_01lsm_"+V1, "HBN_dsn_01lsm_Maatgevende_windr_"+V1, "Hs_bij_HBN_dsn_01lsm_"+V1]        
        insert_cursor = arcpy.da.InsertCursor(Otab,INkols)
    # INkols als 1e regel in de CSV
    #ll.write("SectionEntityId,Vaknaam,"+Hv+"_CalculationEntityId,HBN_"+Hv+"_Hoogte,HBN_"+Hv+"_Maatgevende_windrichting,HBN_"+Hv+"_Golfhoogte_Hs\n")
    ll.write("Vaknaam;HBN_dsn_01lsm_"+V1+";HBN_dsn_01lsm_Maatgevende_windr_"+V1+";Hs_bij_HBN_dsn_01lsm_"+V1+"\n")
    #------------------
    # GrassCoverErosionInwardsSectionResultEntity
    cursor.execute("SELECT "+KOLlijst1+" FROM GrassCoverErosionInwardsSectionResultEntity ORDER BY FailureMechanismSectionEntityId DESC")
    for row0 in cursor.fetchall():
        vaknr = row0[0]
        calcnr = row0[1]
        arcpy.AddMessage("Vaknr:  "+str(vaknr))
        arcpy.AddMessage("Berekeningnr:  "+str(calcnr))
        record = []
        #record.append(vaknr)
        #------------------
        # FailureMechanismSectionEntity uitlezen voor de vaknaam
        cursor.execute("SELECT "+KOLlijst2+" FROM FailureMechanismSectionEntity WHERE FailureMechanismSectionEntityId = "+str(vaknr))
        Rij1 = cursor.fetchall()
        ln1 = len(Rij1)
        if ln1 == 1:        
            for row1 in Rij1:
                record.append(row1[1])
            del row1
        else:
            arcpy.AddWarning("Tabel FailureMechanismSectionEntity bevat geen record voor FailureMechanismSectionEntityId: "+str(nr)+"!\nwaarden op -9999")
            record.append(-9999)
        #------------------
        #record.append(calcnr)
        # Als berekening er is dan verder uitlezen anders alles op 0
        if calcnr != None:
            GRFTilluP = 0
            FTilluP = 0
            WindR = 'None'
            SMillu = 0
            # HBN - GrassCoverErosionInwardsDikeHeightOutputEntity uitlezen    
            cursor.execute("SELECT "+KOLlijst3+" FROM GrassCoverErosionInwardsDikeHeightOutputEntity WHERE GrassCoverErosionInwardsOutputEntityId = "+str(calcnr))
            Rij3 = cursor.fetchall()
            ln3 = len(Rij3)
            # als er een record is dan toevoegen anders x aantal lege waarden toevoegen
            if ln3 == 1:
                for row3 in Rij3:
                    GRFTilluP = row3[1]
                    record.append(row3[2])  # hoogte wegschrijven
                del row3
            else:
                arcpy.AddWarning("Tabel GrassCoverErosionInwardsDikeHeightOutputEntity bevat geen record voor GrassCoverErosionInwardsOutputEntityId: "+str(calcnr)+"!\nwaarden op -9999")
                record.append(-9999)
            #------------------
            if GRFTilluP != None:
                # Maatgevende windrichting - GeneralResultFaultTreeIllustrationPointEntityId uitlezen
                cursor.execute("SELECT "+KOLlijst4+" FROM GeneralResultFaultTreeIllustrationPointEntity WHERE GeneralResultFaultTreeIllustrationPointEntityId = "+str(GRFTilluP))
                Rij4 = cursor.fetchall()
                ln4 = len(Rij4)
                # als er een record is dan toevoegen anders x aantal lege waarden toevoegen
                if ln4 == 1:
                    for row4 in Rij4:
                        WindR = str(row4[1])
                        arcpy.AddMessage("Windrichting:  "+str(WindR))
                        record.append(WindR)
                    del row4
                else:
                    arcpy.AddWarning("Tabel GeneralResultFaultTreeIllustrationPointEntity bevat geen record voor GeneralResultFaultTreeIllustrationPointEntityId: "+str(GRFTilluP)+"!\ngeen windrichting!")
                    record.append("None")
                #------------------
                # Illupunt bij Windrichting - TopLevelFaultTreeIllustrationPointEntity uitlezen
                cursor.execute("SELECT "+KOLlijst5+" FROM TopLevelFaultTreeIllustrationPointEntity WHERE GeneralResultFaultTreeIllustrationPointEntityId = "+str(GRFTilluP)+ " AND WindDirectionName = '"+str(WindR)+"'")
                Rij5 = cursor.fetchall()
                ln5 = len(Rij5)
                # als er een record is dan toevoegen anders x aantal lege waarden toevoegen
                if ln5 == 1:
                    for row5 in Rij5:
                        FTilluP = row5[0]
                    del row5
                else:
                    arcpy.AddWarning("Tabel TopLevelFaultTreeIllustrationPointEntity bevat geen record voor GeneralResultFaultTreeIllustrationPointEntityId: "+str(GRFTilluP)+ " AND WindDirectionName = "+str(WindR)+"!\nwaarden op 0")
                #------------------
                if FTilluP != None:
                    # Submechanism zoeken - FaultTreeSubmechanismIllustrationPointEntity uitlezen
                    cursor.execute("SELECT "+KOLlijst6+" FROM FaultTreeSubmechanismIllustrationPointEntity WHERE FaultTreeIllustrationPointEntityId = "+str(FTilluP))
                    Rij6 = cursor.fetchall()
                    ln6 = len(Rij6)
                    # als er een record is dan toevoegen anders x aantal lege waarden toevoegen
                    # kunnen meerdere records zijn 
                    if ln6 > 0:
                        for row6 in Rij6:
                            # Nu SubM ID opzoeken en kijken welke Overslag RTO is.
                            cursor.execute("SELECT "+KOLlijst7+" FROM SubMechanismIllustrationPointEntity WHERE SubMechanismIllustrationPointEntityId = "+str(row6[0]))
                            Rij6a = cursor.fetchall()
                            ln6a = len(Rij6a)
                            # als er een record is dan toevoegen anders x aantal lege waarden toevoegen
                            # kunnen meerdere records zijn
                            if ln6a > 0:
                                for row6a in Rij6a:
                                    if row6a[1] == 'Overslag RTO':
                                        arcpy.AddMessage("= 'Overslag RTO'")
                                        SMillu = row6a[0]
                        del row6
                    else:
                        arcpy.AddWarning("Tabel FaultTreeSubmechanismIllustrationPointEntity bevat geen record voor FaultTreeIllustrationPointEntityId: "+str(FTilluP)+"!\n")
                    #------------------
                    if SMillu != None:
                        # Golfhoogte(Hs) uitlezen  - IllustrationPointResultEntity uitlezen
                        cursor.execute("SELECT "+KOLlijst8+" FROM IllustrationPointResultEntity WHERE SubMechanismIllustrationPointEntityId = "+str(SMillu)+ " AND Description = 'Golfhoogte (Hs)'")
                        Rij8 = cursor.fetchall()
                        ln8 = len(Rij8)
                        # als er een record is dan toevoegen anders x aantal lege waarden toevoegen
                        if ln8 == 1:
                            for row8 in Rij8:
                                arcpy.AddMessage("Golfhoogte(Hs):  "+str(row8[2]))
                                record.append(row8[2])     # Value Golfhoogte(Hs) wegschrijven.
                            del row8
                        else:
                            arcpy.AddWarning("Tabel IllustrationPointResultEntity bevat geen record voor SubMechanismIllustrationPointEntityId: "+str(SMillu)+ " AND Description = 'Golfhoogte (Hs)'!\nwaarden op -9999")
                            record.append(-9999)
                else:
                    record.append(-9999)
            else:
                record.append("None")
                record.append(-9999)
        #------------------
        else:
            record.append(-9999)
            record.append("None")
            record.append(-9999)
        #-- wegschrijven        
        arcpy.AddMessage("Result: "+str(record))
        arcpy.AddMessage("----------------------------------\n")
        if naarGDB:
            insert_cursor.insertRow(record)
        v = ";".join(str(e).replace('.',',') for e in record)
        ll.write(v+"\n")
        #------------------
    del row0
    cursor.close()
    ll.close()
    try:
        del insert_cursor
    except:
        print ""
else:
    arcpy.AddError("Geen berekening uit te voeren!")
#------------------
arcpy.AddMessage("\n  >>> ----------------------------------")
arcpy.AddMessage("  >>>  KLAAR!  <<<")
arcpy.AddMessage("  >>> ----------------------------------\n")
arcpy.AddMessage("  Resultaten in:")
if naarGDB:
    arcpy.AddMessage(Otab+"\nen\n"+oCSV+"\n")
else:
    arcpy.AddMessage(oCSV+"\n")
