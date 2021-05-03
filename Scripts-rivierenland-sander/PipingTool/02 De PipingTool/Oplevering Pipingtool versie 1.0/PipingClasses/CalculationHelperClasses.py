import os
import xlrd
import arcpy
from collections import OrderedDict



# class KolomLink:
#     def __init__(self, fieldName, propertyName, alias, fieldType="TEXT"):
#         self.FieldName = fieldName
#         self.PropertyName = propertyName
#         self.Alias = alias
#         self.FieldType = fieldType


class TabelKolommenLinksList:
    '''Lijst met kolomlink objecten'''
    def __init__(self, kolommenLinks):
        self.KolommenLinks = kolommenLinks

    def UpdateAliassen(self, tabelPath):
        if arcpy.Exists(tabelPath):
            #   Update de alias voor alle velden

            for kolommenLink in self.KolommenLinks:
                veldnaam = kolommenLink.FieldName
                aanwezigeVelden = arcpy.ListFields(tabelPath, veldnaam)

                if len(aanwezigeVelden) > 0:
                    # aanwezigVeld = aanwezigeVelden[0]
                    print "Set alias for field " + veldnaam
                    arcpy.AlterField_management(tabelPath, veldnaam, new_field_alias=kolommenLink.Alias)

    def GenereerVeldnamenLijst(self):
        '''
        Get list of field names from source table
        :return:
        '''
        veldnamenLijst = []

        for kolomLink in self.KolommenLinks:
            veldnamenLijst.append(kolomLink.FieldName)

        return veldnamenLijst

    def GenereerPropertiesLijst(self):
        propertiesLijst = []

        for kolomLink in self.KolommenLinks:
            propertiesLijst.append(kolomLink.PropertyName)

        return propertiesLijst

    def GenereerVeldnamenKoppeling(self):
        '''
        Generate dictionary linking PropertyNames to FieldNames
        :return:
        '''
        veldnamenKoppeling = dict()
        for kolomLink in self.KolommenLinks:
            veldnamenKoppeling[kolomLink.FieldName] = kolomLink.PropertyName

        return veldnamenKoppeling

    def GenereerVeldtypenKoppeling(self):
        '''
        Generate dictionary linking FieldTypes with FieldNames
        :return:
        '''
        veldtypenKoppeling = OrderedDict()
        for kolomLink in self.KolommenLinks:
            veldtypenKoppeling[kolomLink.FieldName] = kolomLink.FieldType

        return veldtypenKoppeling

    def GenereerPropertyKoppeling(self):
        '''
        Generate dictionary linking FieldNames with PropertyNames
        :return:
        '''

        propertyKoppeling = dict()
        for kolomLink in self.KolommenLinks:
            propertyKoppeling[kolomLink.PropertyName] = kolomLink.FieldName
        return propertyKoppeling

class OutputTabel:

    def __init__(self, tabelPath, outputTabelKolommen,geometryType = None, spatialReference = None):
        self.TabelPath = tabelPath
        self.OutputKolommenList = outputTabelKolommen
        self.GeometryType = geometryType
        self.SpatialReference = spatialReference
        self.TabelRijen = []

    def SchrijfTabelStructuurArcGIS(self):
        #   Maak nieuwe feature class of standalone tabel aan

        outputGdb = os.path.split(self.TabelPath)[0]
        tabelNaam = os.path.split(self.TabelPath)[1]

        if self.GeometryType == None:
            arcpy.CreateTable_management(outputGdb, tabelNaam)
        else:
            arcpy.CreateFeatureclass_management(outputGdb, tabelNaam, geometry_type=self.GeometryType,
                                                spatial_reference=self.SpatialReference)


        #   Loop over kolomDefinities and add fields

        for kolomLink in self.OutputKolommenList.KolommenLinks:
            if kolomLink.FieldName.lower() != "shape":
                if kolomLink.FieldType == "TEKST":
                    kolomLink.FieldType = "TEXT"

                arcpy.AddMessage("Adding field {0} to table {1}".format(kolomLink.FieldName, self.TabelPath))
                arcpy.AddField_management(self.TabelPath, kolomLink.FieldName, kolomLink.FieldType,
                                          field_alias=kolomLink.Alias)


        return




class BasisTabel:
    '''Generieke klasse voor het uitlezen van waarden uit tabellen'''
    def __init__(self, tableName, tabelPath, keyVeldnaam, tabelKolommenLinksListInput, tabelKolommenLinksListOutput):
        self.TableName = tableName
        self.TabelPath = tabelPath
        self.KeyVeldnaam = keyVeldnaam
        self.TabelKolommenLinksListInput = tabelKolommenLinksListInput
        self.TabelKolommenLinksListOutput = tabelKolommenLinksListOutput

        #   Dictionary met dictionaries
        #   Ieder item uit de lijst is een koppeling tussen veldnamen en veldwaardes
        self.TabelRijenDict = dict()

    def LeesTabelRijen(self, whereClause, useXlrd = False):
        #   Doorloop de tabel en genereer een lijst met objecten

        veldnamen = self.TabelKolommenLinksListInput.GenereerVeldnamenLijst()

        #   Controleer welke veldnamen er daadwerkelijk aanwezig zijn

        veldnamenInTabel = []

        if useXlrd == False:
            fieldsCollection = arcpy.ListFields(self.TabelPath)

            for veldnaam in veldnamen:
                for field in fieldsCollection:
                    if field.name == veldnaam:
                        if veldnaam == "Shape":
                            veldnaam = "SHAPE@"

                        veldnamenInTabel.append(veldnaam)
        else:
            #   Use xlrd to read column names in table
            #   First split table path in workbook path and sheetname

            workbookPath = os.path.split(self.TabelPath)[0]
            sheetName = os.path.split(self.TabelPath)[1].replace("$", "")
            sourceExcelWorkbook = xlrd.open_workbook(workbookPath)
            sourceSheet = sourceExcelWorkbook.sheet_by_name(sheetName)

            columnHeaders = sourceSheet.row_values(0)
            for veldnaam in veldnamen:
                for columnHeader in columnHeaders:
                    if columnHeader == veldnaam:
                        veldnamenInTabel.append(veldnaam)

        #   Voeg het keyVeld ook toe aan de uit te lezen kolommen
        veldnamenInTabel.append(self.KeyVeldnaam)
        keyIndex = len(veldnamenInTabel) - 1
        veldnamenKoppeling = self.TabelKolommenLinksListInput.GenereerVeldnamenKoppeling()
        veldnamenKoppeling[self.KeyVeldnaam] = self.KeyVeldnaam

        if useXlrd == False:
            #   Use arcpy SearchCursor to read table contents

            tabelCursor = arcpy.da.SearchCursor(self.TabelPath, veldnamenInTabel, whereClause)

            for tabelRow in tabelCursor:
                #   Lees waarde van het keyField

                keyWaarde = tabelRow[keyIndex]

                fieldValues = dict()

                #   Lees alle relevante kolommen uit

                i = 0

                while i < len(veldnamenInTabel):
                    if veldnamenInTabel[i] == "SHAPE@":
                        fieldValues[veldnamenKoppeling["Shape"]] = tabelRow[i]
                    else:
                        fieldValues[veldnamenKoppeling[veldnamenInTabel[i]]] = tabelRow[i]
                    i += 1

                self.TabelRijenDict[keyWaarde] = fieldValues
            del tabelCursor

            print("{0} rijen uitgelezen".format(len(self.TabelRijenDict)))
        else:

            #   Creating dictionary linking column names to column indices

            colIndicesDict = dict()

            #   Loop over values of first column

            columnHeaders = sourceSheet.row_values(0)
            keyIndex = -1

            for colIndex in range(0, len(columnHeaders)):
                #   Add column name to dictionary if it is contained in veldnamenInTabel

                columnHeader = columnHeaders[colIndex]

                if columnHeader == self.KeyVeldnaam:
                    keyIndex = colIndex

                if veldnamenInTabel.__contains__(columnHeader):
                    colIndicesDict[columnHeader] = colIndex

            if keyIndex == -1:
                print("Key field has not been found, no rows will be returned")
                if useXlrd == True:
                    #   Delete workbook and sheet object
                    del sourceSheet
                    del sourceExcelWorkbook
            else:
                #   Loop through rows of Excel table

                for rowIndex in range(1, sourceSheet.nrows):
                    sheetRow = sourceSheet.row_values(rowIndex)

                    keyWaarde = sheetRow[keyIndex]

                    fieldValues = dict()

                    #   Loop over ColIndicesDict

                    for fieldName in veldnamenInTabel:
                        if fieldName in colIndicesDict.keys():
                            colIndex = colIndicesDict[fieldName]
                            propertyName = veldnamenKoppeling[fieldName]
                            fieldValues[propertyName] = sheetRow[colIndex]

                    self.TabelRijenDict[keyWaarde] = fieldValues

                #   Delete workbook and sheet object
                del sourceSheet
                del sourceExcelWorkbook


    '''Update rijen uit een tabel op basis van de inhoud van dictionaries'''
    def UpdateTabelRijen(self):
        #   Alleen properties van het typeVariabele output worden weggeschreven
        veldtypenKoppeling = self.TabelKolommenLinksListOutput.GenereerVeldtypenKoppeling()
        veldnamenInTabel = self.TabelKolommenLinksListOutput.GenereerVeldnamenLijst()

        #   Controleer welke veldnamen er daadwerkelijk aanwezig zijn

        for veldnaam in veldtypenKoppeling.keys():
            if len(arcpy.ListFields(self.TabelPath, veldnaam)) == 0:
                #   Voeg het veld toe aan de outputFeatureclass
                veldType = veldtypenKoppeling[veldnaam]
                print "Toevoegen veld " + veldnaam + " aan outputFeatureclass " + self.TabelPath
                if veldType == "TEXT":
                    arcpy.AddField_management(self.TabelPath, veldnaam, veldType, field_length=255)
                else:
                    arcpy.AddField_management(self.TabelPath, veldnaam, veldType)

        #   Voeg het keyVeld ook toe aan de uit te lezen kolommen
        veldnamenInTabel.append(self.KeyVeldnaam)
        keyIndex = len(veldnamenInTabel) - 1

        #   Koppeling tussen targetParameter van property en veldnaam in tabel
        propertyKoppeling = self.TabelKolommenLinksListOutput.GenereerPropertyKoppeling()

        #   Koppeling tussen targetParameter van property en index van veld in lijst met (in tabel aanwezig) veldnamen

        indicesKoppeling = dict()

        for propertyName in propertyKoppeling.keys():
            if veldnamenInTabel.__contains__(propertyKoppeling[propertyName]):
                indicesKoppeling[propertyName] = veldnamenInTabel.index(propertyKoppeling[propertyName])

        updateCursor = arcpy.da.UpdateCursor(self.TabelPath, veldnamenInTabel)

        #   Doorloop de complete tabel en kijk per rij of deze voorkomt in het TabelRijenDict

        for updateRij in updateCursor:
            keyWaarde = updateRij[keyIndex]

            if self.TabelRijenDict.has_key(keyWaarde):
                #   Zoek de waarde

                fieldValues = self.TabelRijenDict[keyWaarde]
                for propertyName in indicesKoppeling.keys():
                    #   Dit is de targetParameter van de property, zoek de veldnaam die hierbij hoort

                    if fieldValues.has_key(propertyName):
                        updateRij[indicesKoppeling[propertyName]] = fieldValues[propertyName]

            updateCursor.updateRow(updateRij)
        del updateCursor
        return

    def VulMetDefaultwaarden(self, propertyName, defaultWaarde):
        for keyWaarde in self.TabelRijenDict.keys():
            valuesDict = self.TabelRijenDict[keyWaarde]
            valuesDict[propertyName] = defaultWaarde
        return