# --------------------------------------------------------------------------
# Witteveen+Bos
# ing. H.E.J. Nieuwland - juli 2018
# --------------------------------------------------------------------------
# versie 1.0.0
# --------------------------------------------------------------------------
# Op basis van de GEKB_RapportageTool.mxd de gegevens van de getoetste vakken exporteren naar pdf.
# --------------------------------------------------------------------------
try:
    import arcpy,datetime,sys,traceback
    outPath = sys.argv[1]
    ## instellen map document en outPath
    mxd = arcpy.mapping.MapDocument("CURRENT")
    ## dataframe buiten beeld selecteren tbv loopen door vakken en zoomen naar tbv de inzetkaart
    df0     = arcpy.mapping.ListDataFrames(mxd,"Layers")[0]
    Delijn  = arcpy.mapping.ListLayers(mxd, "prfl_vakken", df0)[0]
    df2     = arcpy.mapping.ListDataFrames(mxd,"Inzetkaart")[0]
    Delijn2 = arcpy.mapping.ListLayers(mxd, "prfl_vakken", df2)[0]
    inGDB  = Delijn.workspacePath
    ## Dwarsprofielen dataframe en lagen zoeken
    df = arcpy.mapping.ListDataFrames(mxd,"DWP")[0]
    prfl_pnt = arcpy.mapping.ListLayers(mxd, "PRFL knikpunten", df)[0]
    prfl_ln  = arcpy.mapping.ListLayers(mxd, "PRFL lijn", df)[0]
    prof_ln  = arcpy.mapping.ListLayers(mxd, "Proflijnen", df)[0]
    ## datum + tijd bepalen tbv pdf-naam
    now   = datetime.datetime.now()
    datum = str(now.strftime("%Y%m%d_%H%M"))
    ## naam pdf 
    finalPdf = arcpy.mapping.PDFDocumentCreate(outPath+"/Rapport_GEKB_"+datum+".pdf")
    ## Export each of the data driven pages
    for pageNum in range(1, mxd.dataDrivenPages.pageCount + 1):
        mxd.dataDrivenPages.currentPageID = pageNum
        ID = mxd.dataDrivenPages.pageRow.getValue ('ID')    
        vaknaam = mxd.dataDrivenPages.pageRow.getValue ('Vaknaam')
        arcpy.AddMessage("ID:  "+str(ID)+"  vaknaam:  "+str(vaknaam))
        ## pannen naar goede extent
        arcpy.SelectLayerByAttribute_management(Delijn, "NEW_SELECTION", "\"ID\" = '"+ID+"'")
        df0.panToExtent(Delijn.getSelectedExtent())
        arcpy.SelectLayerByAttribute_management(Delijn2, "NEW_SELECTION", "\"ID\" = '"+ID+"'")        
        ## Dwarsprofiel updaten de source van de 3 layers updaten obv ID
        try:
            prfl_pnt.replaceDataSource(inGDB,"FILEGDB_WORKSPACE","PRFL_P_"+str(ID))
            prfl_ln.replaceDataSource(inGDB,"FILEGDB_WORKSPACE","PRFL_lijn_"+str(ID))
            prof_ln.replaceDataSource(inGDB,"FILEGDB_WORKSPACE","Lvak_"+str(ID))
            prfl_pnt.visible = True
            prfl_ln.visible = True
            prof_ln.visible = True
        except:
            prfl_pnt.visible = False
            prfl_ln.visible = False
            prof_ln.visible = False
            arcpy.AddMessage("geen dwarsprofiel!")
        #arcpy.RefreshTOC()
        arcpy.RefreshActiveView()
        ## exporteren anar pdf
        arcpy.AddMessage("Verwerken vak {0} van {1}".format(str(mxd.dataDrivenPages.currentPageID), str(mxd.dataDrivenPages.pageCount)))
        ## Kolom uitlezen van de actieve regel van de Index Layer
        arcpy.mapping.ExportToPNG(mxd, outPath+"/Vak_"+str(ID)+".png",resolution=200)
        arcpy.mapping.ExportToPDF(mxd, outPath+"/Vak_"+str(ID)+".pdf")
        finalPdf.appendPages(outPath+"/Vak_"+str(ID)+".pdf")
        # losse PDF's weer verwijderen
        arcpy.Delete_management(outPath+"/Vak_"+str(ID)+".pdf")
        del ID,vaknaam
    ## pdf opslaan
    finalPdf.saveAndClose()
    del mxd,outPath,finalPdf,df,df0,Delijn,inGDB,prfl_pnt,prfl_ln,prof_ln
    arcpy.AddMessage("\n>> KLAAR!")

except arcpy.ExecuteError:
    msgs = arcpy.GetMessages(2)
    arcpy.AddError(msgs)    
#If the error is with the script, or with python, find error and report it to the screen...  
except:
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
    arcpy.AddError(pymsg)
    arcpy.AddError(msgs)


