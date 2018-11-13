# --------------------------------------------------------------------------
# Witteveen+Bos
# ing. H.E.J. Nieuwland - juli 2018
# --------------------------------------------------------------------------
# versie 1.0.0
# --------------------------------------------------------------------------
# Selecteer obv het vakken bestand de representatieve profiellijn per vak uit PWK_GEO_PROFIELLIJNEN
# --------------------------------------------------------------------------
import string, os, sys, locale, arcpy, datetime
# INPUT
VakFC    = sys.argv[1]                 # Vakken FC
vakKol   = "REPROF_NAAM"               # kolom met representatief profiel
toets    = sys.argv[2]                 # naam toetsspoor
uitdir   = sys.argv[3]                 # uitvoer map
kol      = "Segment"                   # kolom Segment = text field!
Proflijn = "PWK_GEO_PROFIELLIJNEN"     # PWK_GEO_PROFIELLIJNEN
PnmKol   = "PROFIELNAAM"               # kolom in PWK_GEO_PROFIELLIJNEN
# meteen de 2 kaarten printen
Kaart1   = "Kaart 1"
Kaart2   = "Kaart 2"
#---
arcpy.env.overwriteOutput = True
arcpy.AddMessage("  >>> -------------------------------------")
arcpy.AddMessage("  >>> "+toets+" rapportage aanmaken... ")
arcpy.AddMessage("  >>> -------------------------------------\n")
#---------------------------------------------------------
#---------------------------------------------------------
# ----  START
#---------------------------------------------------------
# eerst even bepalen hoeveel segmenten er zijn.
SegLijst = []
des = arcpy.Describe(VakFC)  # Als layer anders heet dan de FC
with arcpy.da.SearchCursor(des.catalogPath, [kol]) as cursor2:
    for row2 in cursor2:
        arcpy.AddMessage("segment: "+str(row2[0]))
        SegLijst.append(row2[0])
SegLijst = sorted(set(SegLijst),key=SegLijst.index)
SegLijst = sorted(SegLijst)
arcpy.AddMessage("Er zijn: "+str(len(SegLijst))+" segmenten!\n")
#arcpy.AddMessage("SegLijst: "+str(SegLijst))
naam = VakFC
mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd)[0]
# vakken layer selecteren
Delyr = ''
for lyr in arcpy.mapping.ListLayers(mxd):
    if lyr.name == naam:
        Delyr = lyr
    elif lyr.name == Proflijn:
        dwplyr = lyr
    elif lyr.isGroupLayer:
        if lyr.name == Kaart1:
            K1 = lyr
        elif lyr.name == Kaart2:
            K2 = lyr
## datum + tijd bepalen tbv pdf-naam
now   = datetime.datetime.now()
datum = str(now.strftime("%Y%m%d_%H%M"))
finalPdf1 = arcpy.mapping.PDFDocumentCreate(uitdir+"/Rapport_"+toets+"_TOPO_"+datum+".pdf")
finalPdf2 = arcpy.mapping.PDFDocumentCreate(uitdir+"/Rapport_"+toets+"_DTM_"+datum+".pdf")
# door de segmenten loopen en afbeelding maken.
for seg in SegLijst:
    arcpy.AddMessage("Segment: "+str(seg))
    arcpy.SelectLayerByAttribute_management(in_layer_or_view=Delyr, selection_type="NEW_SELECTION", where_clause=kol+" = '"+str(seg)+"'")    
    df.zoomToSelectedFeatures()
    #-----------------
    # Nu de selected set de repr. profielen uitlezen en selectie op de profiellijnen zetten.
    n = len(list(i for i in arcpy.da.SearchCursor(Delyr, [vakKol])))
    arcpy.AddMessage("Er zijn: "+str(n)+" vakken!\n")
    naamLijst = []
    with arcpy.da.SearchCursor(VakFC, [vakKol]) as cursor2:
        for row2 in cursor2:
            if row2[0] != None and row2[0] != '':
                arcpy.AddMessage("profiel: "+str(row2[0]))
                naamLijst.append(row2[0])
            else:
                arcpy.AddMessage("vak heeft geen representatief profiel!")
    # Nu de definition query er op zetten.
    nm = 0
    for naam in naamLijst:
        nm = nm + 1
        if nm == 1:
            defQ = PnmKol+" = '"+naam+"'"
        else:
            defQ = defQ + " OR "+PnmKol+" = '"+naam+"'"
    #arcpy.AddMessage("defQ: "+str(defQ))
    # Nu de definition query er op zetten.
    dwplyr.definitionQuery = defQ
    arcpy.RefreshActiveView()
    #-----------------
    arcpy.SelectLayerByAttribute_management(in_layer_or_view=Delyr, selection_type="CLEAR_SELECTION")
    Delyr.definitionQuery = kol+" = '"+seg+"'"
    # nu stukje uitzoomen om beter overzicht.
    schaal = long(df.scale) / 1000
    df.scale = long((schaal * 1000) + 10000)
    #arcpy.AddMessage("schaal wordt: "+str(df.scale))
    # nu kaart 1 aanzetten en kaart 2 uit    
    K1.visible = True
    K2.visible = False
    arcpy.RefreshActiveView()
    # naar PNG exporteren
    pngnaam1 = uitdir+"/Segment_"+str(seg)+"_k1.png"
    arcpy.mapping.ExportToPNG(mxd, pngnaam1,resolution=200)    
    # naar PDF exporteren
    pdfnaam1 = uitdir+"/Segment_"+str(seg)+"_k1.pdf"
    arcpy.mapping.ExportToPDF(mxd, pdfnaam1)
    # kaart 1 uit kaart 2 aan.
    K1.visible = False
    K2.visible = True
    arcpy.RefreshActiveView()
    # naar PNG exporteren
    pngnaam2 = uitdir+"/Segment_"+str(seg)+"_k2.png"
    arcpy.mapping.ExportToPNG(mxd, pngnaam2,resolution=200)
    # naar PDF exporteren
    pdfnaam2 = uitdir+"/Segment_"+str(seg)+"_k2.pdf"
    arcpy.mapping.ExportToPDF(mxd, pdfnaam2)
    Delyr.definitionQuery = ""
    finalPdf1.appendPages(pdfnaam1)
    finalPdf2.appendPages(pdfnaam2)
    # losse PDF's weer verwijderen
    arcpy.Delete_management(pdfnaam1)
    arcpy.Delete_management(pdfnaam2)
    arcpy.AddMessage("  >>> -------------------------------------\n")
#-----------------
finalPdf1.saveAndClose()
finalPdf2.saveAndClose()
arcpy.AddMessage("\n  >>>  KLAAR!  <<<")
