import arcpy
import os
from PipingUtilities import CalculationFileUtilities
from PipingClasses import CalculationHelperClasses


featureclassNotExistsMessage = "De feature class {0} bestaat niet."
rasterNotExistsMessage = "Het raster {0} bestaat niet."
wrongFeatureTypeMessage = "De feature class {0} is niet van het type {1}"
fieldMissingMessage = "Het veld {0} is niet aanwezig in de feature class {1}"
excelWorkbookNotExistsMessage = "Het Excel workbook {0} bestaat niet."



def VoegIDVeldToe(outputTabel):

    if len(arcpy.ListFields(outputTabel,"PointID")) == 0:
        arcpy.AddField_management(outputTabel,"PointID",field_type="TEXT",field_length=255)

    updateCursor = arcpy.da.UpdateCursor(outputTabel,["UittredepuntID","Scenarionaam","PointID"])

    for row in updateCursor:
        row[2] = str(row[0]) + "_" + row[1]
        updateCursor.updateRow(row)


    del updateCursor





def VergelijkOutputTabellen(tabelOutput,tabelReferentie,linksListOutput):

    errorMessages = []

    #   Loop over rows of table and compare column values one by one

    for uittredepuntID in tabelReferentie.TabelRijenDict.keys():
        referentieTabelRijDict = tabelReferentie.TabelRijenDict[uittredepuntID]

        #   First check if uittredepuntID is contained in tabelOutput

        if not uittredepuntID in tabelOutput.TabelRijenDict.keys():
            errorMessages.append("Uittredepunt {0} is niet aanwezig in de output tabel")
            continue

        #   Loop over linksListOutput to check column values in correct order

        tabelRijDict = tabelOutput.TabelRijenDict[uittredepuntID]

        for kolomLink in linksListOutput:
            if kolomLink.FieldName in referentieTabelRijDict.keys():
                if kolomLink.FieldName in tabelRijDict.keys():
                    #   Check if values are equal

                    waardeReferentie = referentieTabelRijDict[kolomLink.FieldName]
                    waardeOutput = tabelRijDict[kolomLink.FieldName]

                    if waardeReferentie != waardeOutput:
                        errorMessages.append("De waarde van het veld {0} komt niet overeen voor uittredepunt {1}\nReferentiewaarde: {2}\nWaarde in output: {3}"
                                             .format(kolomLink.FieldName,uittredepuntID,waardeReferentie,waardeOutput))

    return errorMessages


def LeesUittredepuntenFeatureclassAlsBasisTabel(featureclassPath, configuratieTabelInternal):

    #   Lees kolomdefinities

    definitieWorkbookOutput = os.path.split(configuratieTabelInternal)[0]
    definitieSheetnameOutput = os.path.split(configuratieTabelInternal)[1].replace("$", "")

    linksListOutput = CalculationFileUtilities.LeesKolomDefinitiesVoorTemplateXlrd(definitieWorkbookOutput, definitieSheetnameOutput, "Uittredepunten",
                                                          isInput=False)

    # if onlyRequiredParameters == True:
    #     linksListInput, linksListOutput = LeesKolomDefinitiesVoorTemplate(definitieSheetInput, tableName)

    tabelKolommenListInput = CalculationHelperClasses.TabelKolommenLinksList(linksListOutput)
    tabelKolommenListOutput = CalculationHelperClasses.TabelKolommenLinksList(linksListOutput)

    #   Genereer basistabel object voor hectometervakken op basis van kolomdefinities en pad naar basisbestand
    arcpy.AddMessage("Genereren basistabel object")
    basisTabel = CalculationHelperClasses.BasisTabel("Uittredepunten", featureclassPath, "PointID", tabelKolommenListInput,
                                                     tabelKolommenListOutput)

    #   Lees alle data uit
    arcpy.AddMessage("Uitlezen rijen tabel " + featureclassPath)

    #   Check if tabelPath contains extensions .xlsx
    #   In this case, xlrd library should be used to read the table contents

    inExcelSource = False

    if ".xlsx" in featureclassPath or ".xlsm" in featureclassPath:
        inExcelSource = True

    basisTabel.LeesTabelRijen(whereClause=None, useXlrd=inExcelSource)

    #   Loop over rows and read values

    for uittredepuntID in basisTabel.TabelRijenDict.keys():
        tabelRijDict = basisTabel.TabelRijenDict[uittredepuntID]

        #   Loop over linksListOutput to check column values in correct order

        for kolomLink in linksListOutput:
            if kolomLink.FieldName in tabelRijDict.keys():
                print("Waarde van kolom {0} : {1}".format(kolomLink.FieldName,tabelRijDict[kolomLink.FieldName]))


    return basisTabel,linksListOutput




def ValidateFeatureclass(featureclassPath,requiredFeatureType = None,requiredFields = None):

    #   First check if feature class exists on disk

    if arcpy.Exists(featureclassPath):
        #   Check feature type

        if requiredFeatureType != None:
            description = arcpy.Describe(featureclassPath)

            if description.shapeType != requiredFeatureType:
                return [False,wrongFeatureTypeMessage.format(featureclassPath,requiredFeatureType)]

        #   Check if one or more required fields exist
        if requiredFields != None:
            for requiredField in requiredFields:
                if len(arcpy.ListFields(featureclassPath,requiredField)) == 0:
                    return [False, fieldMissingMessage.format(requiredField,featureclassPath,)]


    else:
        return [False, featureclassNotExistsMessage.format(featureclassPath)]



    return [True,""]


def ValidateRaster(rasterPath):

    if not arcpy.Exists(rasterPath):
        return [False,rasterNotExistsMessage.format(rasterPath)]
    return [True,""]

def ValidateWorkbook(workbookPath):

    if not os.path.isfile(workbookPath):
        return [False,excelWorkbookNotExistsMessage.format(workbookPath)]

    return [True,""]




def ValideerTestresultaten(testdataRootfolder = None):

    scriptingRootFolder = os.path.split(os.path.dirname(__file__))[0]

    if testdataRootfolder == None:
        testdataRootfolder = scriptingRootFolder + r"\Testdata"

    testOutputFeatureclass = testdataRootfolder + r"\Output.gdb\OutputPipingCalculationScenarios"
    referentieOutputFeatureclass = testdataRootfolder + r"\Output_referentie.gdb\OutputPipingCalculationScenarios"
    configuratieTabelInternal = scriptingRootFolder + r"\Configuratietabel\ConfiguratieInputsOutputs.xlsm\Outputs"

    #   Add unique ID field to output point featureclasses

    VoegIDVeldToe(testOutputFeatureclass)
    VoegIDVeldToe(referentieOutputFeatureclass)

    #   Compare tables

    outputTabel, linksListOutput = LeesUittredepuntenFeatureclassAlsBasisTabel(testOutputFeatureclass,
                                                                               configuratieTabelInternal)
    referentieTabel, linksListOutput = LeesUittredepuntenFeatureclassAlsBasisTabel(referentieOutputFeatureclass,
                                                                                   configuratieTabelInternal)

    errorMessages = VergelijkOutputTabellen(outputTabel, referentieTabel, linksListOutput)

    testResult = True



    return testResult, errorMessages