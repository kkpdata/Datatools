import datetime
import xlrd
import PipingCalculationConfig
import arcpy

calculationConfigSheetname = "CalculationSettings"

def GetNamedRangeValueSingle(workbookPath, namedRangeName):
    workbook = xlrd.open_workbook(workbookPath)

    namedRangesDict = workbook.name_map

    for namedRangeTuple in namedRangesDict.keys():
        namedRange = namedRangesDict[namedRangeTuple][0]

        if namedRange.name == namedRangeName:
            formulaText = namedRange.formula_text

            values = GetValuesFromFormula(workbook, formulaText)
            del workbook
            return values

    del workbook
    return None, None, None, None


def GetColIndex(worksheet, colName):
    for colIndex in range (0,worksheet.ncols):
        if xlrd.colname(colIndex) == colName:
            return colIndex

    return -1


def GetValuesFromFormula(configurationBook, formula):
    '''
    Get single value or arrays of values from cell address or cell range
    :param configurationBook:
    :param formula:
    :return:
    '''

    formulaParts = formula.split("!")

    try:
        sheetName = formulaParts[0]
        rangeParts = formulaParts[1].split(":")

        worksheet = configurationBook.sheet_by_name(sheetName)

        if len(rangeParts) == 1:
            #   Single cell reference

            addressParts = rangeParts[0].split("$")
            colName = addressParts[1]
            rowIndex = int(addressParts[2]) - 1
            colIndex = GetColIndex(worksheet, colName)

            celValue = worksheet.cell(rowIndex, colIndex).value
            return True, True, celValue, sheetName


        else:
            #   Get location of start and end of range

            startAddressParts = rangeParts[0].split("$")
            startColName = startAddressParts[1]
            startColIndex = GetColIndex(worksheet, startColName)
            startRowIndex = int(startAddressParts[2])

            endAddressParts = rangeParts[1].split("$")
            endColName = endAddressParts[1]
            endColIndex = GetColIndex(worksheet, endColName)
            endRowIndex = int(endAddressParts[2])

            rangeColValuesCollection = []

            for colIndex in range(startColIndex, endColIndex + 1):
                rangeColValues = []

                for rowIndex in range(startRowIndex - 1, endRowIndex):
                    rangeColValues.append(worksheet.cell(rowIndex, colIndex).value)

                rangeColValuesCollection.append(rangeColValues)

            return True, False, rangeColValuesCollection, sheetName
    except:
        return False, None, None, None



def UpdateCalculationSettings(workbookPath):

    configurationBook = xlrd.open_workbook(workbookPath)

    namedRangesCollection = configurationBook.name_map
    calculationVariableDict = dict()

    for namedRangeNameKey in namedRangesCollection.keys():
        namedRangeObject = namedRangesCollection[namedRangeNameKey]
        namedRangeName = namedRangeObject[0].name

        arcpy.AddMessage("Reading values for Named range {0}".format(namedRangeName))

        # arcpy.AddMessage(namedRangeName.name)
        namedRangeValueOutComes = GetNamedRangeValueSingle(workbookPath,namedRangeName)

        #   Tuple contains following items:
        #   Index 0: named range is present?
        #   Index 1: named range is single value or not?
        #   Index 2: values of named range (scalar or array of column values)

        if namedRangeValueOutComes[0] == True:
            isSingleCell = namedRangeValueOutComes[1]
            namedRangeValue = namedRangeValueOutComes[2]
            namedRangeSheetName = namedRangeValueOutComes[3]

            #   Check if variable is present in PipingCalculationConfig

            if isSingleCell == True and namedRangeSheetName == calculationConfigSheetname:
                calculationVariableDict[namedRangeName] = namedRangeValue
        else:
            arcpy.AddMessage("Error in reading named range {0}".format(namedRangeName))



    del configurationBook

    #   Check if calculation settings exist in PipingCalculationConfig

    for variableName in calculationVariableDict.keys():
        variableValue = calculationVariableDict[variableName]

        if variableName in PipingCalculationConfig.__dict__:
            #   Update value in PipingCalculationConfig
            arcpy.AddMessage("Variable {0} is present in PipingCalculationConfig".format(variableName))
            setattr(PipingCalculationConfig, variableName, variableValue)
        else:
            arcpy.AddMessage("Variable {0} is missing in PipingCalculationConfig".format(variableName))

