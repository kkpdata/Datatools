import os
import arcpy
import xlrd
import InputConfig
from PipingClasses import CalculationHelperClasses
from PipingClasses import PipingCalculationClasses
from PipingUtilities import PipingGeoprocessingUtilities
from PipingClasses import TemplateClasses


def SchrijfResultatenArcGISPoints(outputTablePath, outputKolommenList, pipingCalculationScenarios, spatialReference):
    outputTabel = CalculationHelperClasses.OutputTabel(outputTablePath, outputKolommenList, geometryType="POINT",
                                                       spatialReference=spatialReference)

    #   Maak lege velden aan in de tabel

    outputTabel.SchrijfTabelStructuurArcGIS()

    #   Loop over pipingCalculationScenarios en schrijf de properties weg

    #   Alleen properties van het typeVariabele output worden weggeschreven

    veldnamenInTabel = outputKolommenList.GenereerVeldnamenLijst()

    veldTypenKoppeling = outputKolommenList.GenereerVeldtypenKoppeling()

    #   Koppeling tussen targetParameter van property en veldnaam in tabel
    propertyKoppeling = outputKolommenList.GenereerPropertyKoppeling()

    #   Koppeling tussen targetParameter van property en index van veld in lijst met (in tabel aanwezig) veldnamen

    indicesKoppeling = dict()

    for propertyName in propertyKoppeling.keys():
        if veldnamenInTabel.__contains__(propertyKoppeling[propertyName]):
            indicesKoppeling[propertyName] = veldnamenInTabel.index(propertyKoppeling[propertyName])

    insertCursor = arcpy.da.InsertCursor(outputTablePath, veldnamenInTabel)

    #   Doorloop de complete tabel en kijk per rij of deze voorkomt in het TabelRijenDict

    propNames = outputKolommenList.GenereerPropertiesLijst()

    for pipingCalculationScenario in pipingCalculationScenarios:
        #   Update properties in Tabelrij dictionary
        pipingCalculationScenario.UpdateOutputProps(propNames)

        #   Maak lege lijst

        insertItems = [None] * len(veldnamenInTabel)

        #   Zoek de waarde

        fieldValues = pipingCalculationScenario.TabelRij
        for propertyName in indicesKoppeling.keys():
            #   Dit is de targetParameter van de property, zoek de veldnaam die hierbij hoort

            fieldName = propertyKoppeling[propertyName]
            fieldType = veldTypenKoppeling[fieldName]

            if fieldValues.has_key(propertyName):

                fieldValue = fieldValues[propertyName]

                if fieldType == "DOUBLE":
                    try:
                        fieldValue = float(fieldValue)
                    except:
                        fieldValue = -9999.0
                elif fieldType == "INTEGER":
                    try:
                        fieldValue = int(fieldValue)
                    except:
                        fieldValue = -9999
                insertItems[indicesKoppeling[propertyName]] = fieldValue
            else:
                arcpy.AddMessage("Property {0} is missing".format(propertyName))

        insertCursor.insertRow(insertItems)
    del insertCursor


def MergeUittredepuntenEnOndergrondScenarios(outputTablePath, basisTabelIntredepunten, basisTabelOndergrondScenarios, pipingCalculationScenarios, spatialReference = None):
    #   Voeg de input- en outputkolommen van intredepunten en ondergrondscenarios samen

    mergedOutputKolommen = []

    kolommenSets = [basisTabelIntredepunten.TabelKolommenLinksListOutput, basisTabelOndergrondScenarios.TabelKolommenLinksListOutput]

    for kolommenSet in kolommenSets:
        for kolomLink in kolommenSet.KolommenLinks:
            #  Controleer of de kolom al aanwezig is op basis van PropertyName

            if len(filter(lambda k:k.PropertyName == kolomLink.PropertyName,mergedOutputKolommen)) == 0:
                mergedOutputKolommen.append(kolomLink)

    #   Sorteer de output kolommen op basis van ColumnIndex

    mergedOutputKolommen.sort(key=lambda k: k.ColumnIndex)

    #   Maak nieuw outputTabel object aan

    outputKolommenList = CalculationHelperClasses.TabelKolommenLinksList(mergedOutputKolommen)

    SchrijfResultatenArcGISPoints(outputTablePath, outputKolommenList, pipingCalculationScenarios, spatialReference)
    return


def GenereerAggregatie(outputTablePath, kolomDefinitiesAggregatie, pipingCalculationResultaten, spatialReference):

    arcpy.AddMessage("Genereren aggregatie per uittredepunt in tabel {0}".format(outputTablePath))
    kolommenListAggregatie = CalculationHelperClasses.TabelKolommenLinksList(kolomDefinitiesAggregatie)

    SchrijfResultatenArcGISPoints(outputTablePath, kolommenListAggregatie, pipingCalculationResultaten, spatialReference)


    return




# def LeesKolomDefinities(definitieSheet, tableName):
#     '''Lees link tussen kolomnamen, property names en aliassen'''
#     kolommenLinksInput = []
#     kolommenLinksOutput = []
#
#     #   Lees eerst de (statische) properties van de tabellen uit
#     #   Deze worden niet door de analyses gewijzigd
#     sheetCursor = arcpy.SearchCursor(definitieSheet, "Tablename = '" + tableName + "'")
#
#     for sheetRow in sheetCursor:
#         veldNaam = sheetRow.getValue("FieldName")
#         propertyNaam = sheetRow.getValue("PropertyName")
#         alias = sheetRow.getValue("Alias")
#         direction = sheetRow.getValue("Direction")
#         fieldType = sheetRow.getValue("FieldType")
#
#         if fieldType == "TEKST":
#             fieldType = "TEXT"
#
#         if propertyNaam is not None and alias != "":
#             #   Deze kolom moet gelinkt worden
#
#             if direction == "Output":
#                 #   In dit geval is het veldtype belangrijk
#
#                 nieuweLink = CalculationHelperClasses.KolomLink(veldNaam, propertyNaam, alias, fieldType)
#                 kolommenLinksOutput.append(nieuweLink)
#
#             else:
#                 nieuweLink = CalculationHelperClasses.KolomLink(veldNaam, propertyNaam, alias, fieldType)
#                 kolommenLinksInput.append(nieuweLink)
#
#     del sheetCursor
#
#     return kolommenLinksInput, kolommenLinksOutput

def LeesKolomDefinitiesVoorTemplate(definitieSheet, tableName, isInput = True):
    '''Lees link tussen kolomnamen, property names en aliassen'''
    kolomDefinities = []

    direction = "Input"

    if isInput == False:
        direction = "Output"

    #kolommenLinksOutput = []

    #   Lees eerst de (statische) properties van de tabellen uit
    #   Deze worden niet door de analyses gewijzigd
    sheetCursor = arcpy.SearchCursor(definitieSheet, "Tablename = '" + tableName + "'")

    for sheetRow in sheetCursor:
        veldNaam = sheetRow.getValue("FieldName")
        propertyNaam = sheetRow.getValue("PropertyName")
        alias = sheetRow.getValue("Alias")
        directionForRow = sheetRow.getValue("Direction")
        fieldType = sheetRow.getValue("FieldType")
        #isRequired = sheetRow.getValue("OpnemenInOutput")

        isRequired = 1
        typeKoppeling = sheetRow.getValue("TypeKoppeling")
        inputBestand = sheetRow.getValue("InputBestand")
        inputKolom = sheetRow.getValue("InputVeldnaam")
        whereClause = sheetRow.getValue("WhereClause")



        if fieldType == "TEKST":
            fieldType = "TEXT"

        if propertyNaam is not None and alias != "":
            #   Deze kolom moet gelinkt worden

            if directionForRow == direction:
                includeColumn = True

                if int(isRequired == 0) and (typeKoppeling == None or typeKoppeling == ""):
                    includeColumn = False

                if includeColumn:
                    kolomDefinitie = TemplateClasses.KolomDefinitie(veldNaam, fieldType, alias, typeKoppeling, inputBestand, inputKolom, whereClause, propertyName=propertyNaam)
                    kolomDefinities.append(kolomDefinitie)

    del sheetCursor

    return kolomDefinities


def LeesKolomDefinitiesVoorTemplateXlrd(definitieWorkbook, sheetName, tableName, isInput = True):
    '''Lees link tussen kolomnamen, property names en aliassen'''
    kolomDefinities = []

    excelWorkbook = xlrd.open_workbook(definitieWorkbook)
    definitionSheet = excelWorkbook.sheet_by_name(sheetName)

    #   Maak dictionary met kolomnamen en indices

    colIndicesDict = dict()

    #   Loop over values of first column

    columnNames = definitionSheet.row_values(0)

    for colIndex in range(0, len(columnNames)):
        colIndicesDict[columnNames[colIndex]] = colIndex


    direction = "Input"

    if isInput == False:
        direction = "Output"

    #   Loop door rijen van Excel tabblad

    for rowIndex in range(1,definitionSheet.nrows):
        sheetRow = definitionSheet.row_values(rowIndex)

        tableNameForRow = sheetRow[colIndicesDict["TableName"]]

        if tableNameForRow == tableName:
            veldNaam = sheetRow[colIndicesDict["FieldName"]]
            propertyNaam = sheetRow[colIndicesDict["PropertyName"]]
            alias = sheetRow[colIndicesDict["Alias"]]
            directionForRow = sheetRow[colIndicesDict["Direction"]]
            fieldType = sheetRow[colIndicesDict["FieldType"]]
            #isRequired = sheetRow[colIndicesDict["OpnemenInOutput"]]

            isRequired = 1
            typeKoppeling = sheetRow[colIndicesDict["TypeKoppeling"]]
            inputBestand = sheetRow[colIndicesDict["InputBestand"]]
            inputKolom = sheetRow[colIndicesDict["InputVeldnaam"]]
            whereClause = sheetRow[colIndicesDict["WhereClause"]]
            columnIndex = -1

            if "ColumnIndex" in colIndicesDict.keys():
                try:
                    columnIndex = int(sheetRow[colIndicesDict["ColumnIndex"]])
                except:
                    arcpy.AddMessage("Error in parsing value {0} to integer".format(colIndicesDict["ColumnIndex"]))


            # veldNaam = sheetRow.getValue("FieldName")
            # propertyNaam = sheetRow.getValue("PropertyName")
            # alias = sheetRow.getValue("Alias")
            # directionForRow = sheetRow.getValue("Direction")
            # fieldType = sheetRow.getValue("FieldType")
            # isRequired = sheetRow.getValue("OpnemenInOutput")
            # typeKoppeling = sheetRow.getValue("TypeKoppeling")
            # inputBestand = sheetRow.getValue("InputBestand")
            # inputKolom = sheetRow.getValue("InputVeldnaam")
            # whereClause = sheetRow.getValue("WhereClause")

            if fieldType == "TEKST":
                fieldType = "TEXT"

            if propertyNaam is not None and alias != "":
                #   Deze kolom moet gelinkt worden

                if directionForRow == direction:
                    includeColumn = True

                    if int(isRequired == 0) and (typeKoppeling == None or typeKoppeling == ""):
                        includeColumn = False

                    if includeColumn:
                        kolomDefinitie = TemplateClasses.KolomDefinitie(veldNaam, fieldType, alias, typeKoppeling, inputBestand, inputKolom, whereClause, propertyName=propertyNaam, columnIndex=columnIndex)
                        kolomDefinities.append(kolomDefinitie)

    del definitionSheet
    del definitieWorkbook

    return kolomDefinities



def LeesBestandIn(tableName, keyVeldnaam, tabelPath, definitieSheetInput, definitieSheetOutput, onlyRequiredParameters = False):
    '''
    Lees tabel in als BasisTabel object
    :param tableName:
    :param keyVeldnaam:
    :param tabelPath:
    :param definitieSheetInput:
    :param definitieSheetOutput:
    :param onlyRequiredParameters:
    :return:
    '''
    #   Lees kolomdefinities

    arcpy.AddMessage("Uitlezen kolomdefinities input uit sheet " + definitieSheetInput)

    definitieWorkbookInput = os.path.split(definitieSheetInput)[0]
    definitieSheetname = os.path.split(definitieSheetInput)[1].replace("$","")

    definitieWorkbookOutput = os.path.split(definitieSheetOutput)[0]
    definitieSheetnameOutput = os.path.split(definitieSheetOutput)[1].replace("$", "")

    linksListInput = LeesKolomDefinitiesVoorTemplateXlrd(definitieWorkbookInput, definitieSheetname, tableName, isInput=True)
    linksListOutput = LeesKolomDefinitiesVoorTemplateXlrd(definitieWorkbookOutput, definitieSheetnameOutput, tableName, isInput=False)

    tabelKolommenListInput = CalculationHelperClasses.TabelKolommenLinksList(linksListInput)
    tabelKolommenListOutput = CalculationHelperClasses.TabelKolommenLinksList(linksListOutput)

    #   Genereer basistabel object voor hectometervakken op basis van kolomdefinities en pad naar basisbestand
    arcpy.AddMessage("Genereren basistabel object")
    basisTabel = CalculationHelperClasses.BasisTabel(tableName, tabelPath, keyVeldnaam, tabelKolommenListInput, tabelKolommenListOutput)

    #   Lees alle data uit
    arcpy.AddMessage("Uitlezen rijen tabel " + tabelPath)

    #   Check if tabelPath contains extensions .xlsx
    #   In this case, xlrd library should be used to read the table contents

    inExcelSource = False

    if ".xlsx" in tabelPath or ".xlsm" in tabelPath:
        inExcelSource = True

    basisTabel.LeesTabelRijen(whereClause=None, useXlrd=inExcelSource)

    return basisTabel

