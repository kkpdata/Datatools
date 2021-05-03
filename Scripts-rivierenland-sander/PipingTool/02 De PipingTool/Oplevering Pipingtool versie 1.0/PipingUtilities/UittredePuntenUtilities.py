import os
import arcpy
import InputConfig
from PipingUtilities import ValidationUtilities

from PipingUtilities import CalculationFileUtilities, CreateTemplates

spatialReference = arcpy.SpatialReference("RD New")
numberFieldName = "UittredepuntenID"

def KopieerGeometrie(basisbestandInput, uittredepuntenFeatureclass):
    #   Kopieer de geometrie en een opmerking vanuit het basisbestand

    arcpy.AddMessage("Kopieer input vanuit {0} naar {1}".format(basisbestandInput,uittredepuntenFeatureclass))

    pointsSearchCursor = arcpy.da.SearchCursor(basisbestandInput, ["SHAPE@", "Opmerking_uittredepunt"])
    pointsInsertCursor = arcpy.da.InsertCursor(uittredepuntenFeatureclass, ["SHAPE@", "Opmerking_uittredepunt"])

    for pointRow in pointsSearchCursor:
        pointsInsertCursor.insertRow([pointRow[0], pointRow[1]])

    del pointsSearchCursor
    del pointsInsertCursor


def VulPuntNummers(uittredepuntenFeatureclass):

    arcpy.AddMessage("Toekennen unieke nummers aan punten in featureclass {0}".format(uittredepuntenFeatureclass))
    updateCursor = arcpy.da.UpdateCursor(uittredepuntenFeatureclass, ["OID@","UittredepuntenID"])

    for updateRow in updateCursor:
        updateRow[1] = updateRow[0]
        updateCursor.updateRow(updateRow)

    del updateCursor


def ValideerKolomdefinities(kolomDefinities):

    validationResults = []

    #   Valideer SpatialJoin kolommen

    kolommenSpatialJoin = list(filter(lambda k: k.LinkType == "SpatialJoin" and k.SourceDataset != None and k.SourceDataset != "",kolomDefinities))

    for kolomSpatialJoin in kolommenSpatialJoin:
        #   Check if source dataset exists, and has the required geometry type

        fieldNames = None

        if kolomSpatialJoin.InputFieldName != "Distance":
            fieldNames = [kolomSpatialJoin.InputFieldName]
        validationResult = ValidationUtilities.ValidateFeatureclass(kolomSpatialJoin.SourceDataset,requiredFields=fieldNames)
        validationResults.append(validationResult)

    #   Valideer Raster kolommen

    kolommenRaster = list(filter(lambda k: k.LinkType == "RasterWaarde" and k.SourceDataset != None and k.SourceDataset != "", kolomDefinities))

    for kolomRaster in kolommenRaster:
        #   Check if source dataset exists, and has the required geometry type
        validationResult = ValidationUtilities.ValidateRaster(kolomRaster.SourceDataset)
        validationResults.append(validationResult)


    #   Check if there validation errors

    #   Check if inputs are valid

    validationResultsWithError = list(filter(lambda v: v[0] == False, validationResults))

    if len(validationResultsWithError) > 0:
        for validationResult in validationResultsWithError:
            arcpy.AddWarning(validationResult[1])
        return False

    return True



def VulSpatialJoinKolommen(uittredepuntenFeatureclass, kolomDefinities, outputGdb, intermediateResults):

    uittredepuntenFeatureclassNaam = os.path.split(uittredepuntenFeatureclass)[1]

    kolommenSpatialJoin = list(filter(lambda k:k.LinkType == "SpatialJoin" and k.SourceDataset != None and k.SourceDataset != "", kolomDefinities))

    for kolomSpatialJoin in kolommenSpatialJoin:
        #   Maak kopie van origineel

        sourceFeatureclassName = os.path.split(kolomSpatialJoin.SourceDataset)[1]

        outputName = sourceFeatureclassName + "_" + kolomSpatialJoin.FieldName

        copyFeatureclass = outputGdb + os.sep + outputName
        intermediateResults.append(copyFeatureclass)

        arcpy.AddMessage("Copy featureclass {0} to {1}".format(kolomSpatialJoin.SourceDataset, copyFeatureclass))

        if kolomSpatialJoin.WhereClause != None and kolomSpatialJoin.WhereClause != "":
            arcpy.Select_analysis(kolomSpatialJoin.SourceDataset, copyFeatureclass, where_clause=kolomSpatialJoin.WhereClause)
        else:
            arcpy.Select_analysis(kolomSpatialJoin.SourceDataset, copyFeatureclass)

        #   Stel projectie in om ervoor te zorgen dat de Spatial Join uitgevoerd kan worden

        arcpy.DefineProjection_management(copyFeatureclass, spatialReference)

        arcpy.AddMessage("Spatial join {0} to points {1}".format(copyFeatureclass,uittredepuntenFeatureclass))
        spatialJoinOutput = outputGdb + os.sep + uittredepuntenFeatureclassNaam + "_join_" + outputName
        arcpy.SpatialJoin_analysis(uittredepuntenFeatureclass, copyFeatureclass, spatialJoinOutput, join_operation="JOIN_ONE_TO_ONE", match_option="CLOSEST",distance_field_name="ClosestDistance")
        intermediateResults.append(spatialJoinOutput)

        #   Maak dictionary met puntnummer als key en attribuutwaarden als values

        valueLinkDict = dict()

        fields = [numberFieldName,kolomSpatialJoin.InputFieldName]

        if kolomSpatialJoin.InputFieldName == "Distance":
            fields = [numberFieldName,"ClosestDistance"]

        duplicateFieldName = kolomSpatialJoin.InputFieldName + "_1"

        if len(arcpy.ListFields(spatialJoinOutput, duplicateFieldName)) == 1:
            arcpy.AddMessage("Column name {0} was already present before running spatial join, looking for column {1} instead".format(kolomSpatialJoin.InputFieldName, duplicateFieldName))
            fields = [numberFieldName, duplicateFieldName]


        spatialJoinCursor = arcpy.da.SearchCursor(spatialJoinOutput,fields)

        for spatialJoinRow in spatialJoinCursor:
            valueLinkDict[spatialJoinRow[0]] = spatialJoinRow[1]

        del spatialJoinCursor


        #   Update waardes in uittredepuntenFeatureclass

        arcpy.AddMessage("Update values in field {0} in featureclass {1}".format(kolomSpatialJoin.FieldName,uittredepuntenFeatureclass))

        pointsUpdateCursor = arcpy.da.UpdateCursor(uittredepuntenFeatureclass,[numberFieldName,kolomSpatialJoin.FieldName])

        for pointRow in pointsUpdateCursor:
            pointNr = pointRow[0]

            if pointNr in valueLinkDict.keys():
                pointRow[1] = valueLinkDict[pointNr]
                pointsUpdateCursor.updateRow(pointRow)

        del pointsUpdateCursor


def VulRasterwaardeKolommen(uittredepuntenFeatureclass, kolomDefinities, outputGdb, intermediateResults):

    arcpy.CheckOutExtension("Spatial")

    kolommenRasterWaarde = list(filter(lambda k:k.LinkType == "RasterWaarde" and k.SourceDataset!= None and k.SourceDataset != "", kolomDefinities))

    for kolomRasterWaarde in kolommenRasterWaarde:
        #   Maak kopie van origineel

        sourceRasterName = os.path.split(kolomRasterWaarde.SourceDataset)[1]

        outputName = sourceRasterName + "_" + kolomRasterWaarde.FieldName

        extractFeatureclass = outputGdb + os.sep + outputName

        arcpy.AddMessage("Extract values from raster {0} to featureclass {1}".format(kolomRasterWaarde.SourceDataset, extractFeatureclass))

        arcpy.sa.ExtractValuesToPoints(uittredepuntenFeatureclass,kolomRasterWaarde.SourceDataset,extractFeatureclass)
        intermediateResults.append(extractFeatureclass)

        #   Maak dictionary met puntnummer als key en attribuutwaarden als values

        valueLinkDict = dict()

        fields = [numberFieldName,"RASTERVALU"]


        extractResultCursor = arcpy.da.SearchCursor(extractFeatureclass,fields)

        for spatialJoinRow in extractResultCursor:
            valueLinkDict[spatialJoinRow[0]] = spatialJoinRow[1]

        del extractResultCursor


        #   Update waardes in uittredepuntenFeatureclass

        arcpy.AddMessage("Update values in field {0} in featureclass {1}".format(kolomRasterWaarde.FieldName,uittredepuntenFeatureclass))

        pointsUpdateCursor = arcpy.da.UpdateCursor(uittredepuntenFeatureclass,[numberFieldName,kolomRasterWaarde.FieldName])

        for pointRow in pointsUpdateCursor:
            pointNr = pointRow[0]

            if pointNr in valueLinkDict.keys():
                pointRow[1] = valueLinkDict[pointNr]
                pointsUpdateCursor.updateRow(pointRow)

        del pointsUpdateCursor

    arcpy.CheckExtension("Spatial")


def VulSpecifiekeKolommen(uittredepuntenFeatureclass, kolomDefinities, outputGdb):
    uittredepuntenFeatureclassNaam = os.path.split(uittredepuntenFeatureclass)[1]

    kolommenSpecifiek = list(filter(lambda k: k.LinkType == "Specifiek" and k.SourceDataset != None and k.SourceDataset != "",kolomDefinities))

    for kolomSpecifiek in kolommenSpecifiek:
        functionName = kolomSpecifiek.InputFieldName

        #   Maak een eval statement op basis van de functienaam

        eval("{0}(uittredepuntenFeatureclass, kolomSpecifiek, outputGdb)".format(functionName))



    return




def BepaalPeilgebieden(uittredepuntenFeatureclass, kolomSpecifiek, outputGdb):

    #   Maak kopie van input featureclass

    sourceFeatureclassName = os.path.split(kolomSpecifiek.SourceDataset)[1]

    outputName = sourceFeatureclassName + "_" + kolomSpecifiek.FieldName

    copyFeatureclass = outputGdb + os.sep + outputName

    arcpy.AddMessage("Copy featureclass {0} to {1}".format(kolomSpecifiek.SourceDataset, copyFeatureclass))

    if kolomSpecifiek.WhereClause != None and kolomSpecifiek.WhereClause != "":
        arcpy.Select_analysis(kolomSpecifiek.SourceDataset, copyFeatureclass,
                              where_clause=kolomSpecifiek.WhereClause)
    else:
        arcpy.Select_analysis(kolomSpecifiek.SourceDataset, copyFeatureclass)

    #   Stel projectie in om ervoor te zorgen dat de Spatial Join uitgevoerd kan worden

    arcpy.DefineProjection_management(copyFeatureclass, spatialReference)

    arcpy.AddMessage("Spatial join {0} to points {1}".format(copyFeatureclass, uittredepuntenFeatureclass))

    uittredepuntenFeatureclassNaam = os.path.split(uittredepuntenFeatureclass)[1]

    spatialJoinOutput = outputGdb + os.sep + uittredepuntenFeatureclassNaam + "_join_" + outputName
    arcpy.SpatialJoin_analysis(uittredepuntenFeatureclass, copyFeatureclass, spatialJoinOutput, join_operation="JOIN_ONE_TO_ONE", match_option="CLOSEST", distance_field_name="ClosestDistance")

    valueLinkDict = dict()

    fields = [numberFieldName,"zomerpeil","winterpeil","VASTPEIL"]


    spatialJoinCursor = arcpy.da.SearchCursor(spatialJoinOutput, fields)

    for spatialJoinRow in spatialJoinCursor:
        #   Controleer of er een vast peil ingevuld is

        puntNr = spatialJoinRow[0]
        peil = spatialJoinRow[3]
        typePeil = "vast"

        if peil == None:
            peil = spatialJoinRow[2]
            typePeil = "seizoensgebonden"

        valueLinkDict[puntNr] = [peil, typePeil]

    del spatialJoinCursor

    updateFields = [numberFieldName,kolomSpecifiek.FieldName]
    typeFieldPresent = False

    if len(arcpy.ListFields(uittredepuntenFeatureclass,"Polderpeil_Type")) == 1:
        updateFields.append("Polderpeil_Type")
        typeFieldPresent = True

    pointsUpdateCursor = arcpy.da.UpdateCursor(uittredepuntenFeatureclass,updateFields)

    for pointRow in pointsUpdateCursor:
        pointNr = pointRow[0]

        if pointNr in valueLinkDict.keys():
            pointRow[1] = valueLinkDict[pointNr][0]
            if typeFieldPresent:
                pointRow[2] = valueLinkDict[pointNr][1]

            pointsUpdateCursor.updateRow(pointRow)
    del pointsUpdateCursor

    return














