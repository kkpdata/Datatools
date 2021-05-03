import arcpy
import os
import InputConfig
from PipingUtilities import CalculationFileUtilities,CreateTemplates
from PipingUtilities import ValidationUtilities
from TestScripts import VulUittredePunten



def ValidateInputsTemplate(configurationWorkbookPath):
    validationResults = []

    validationResults.append(ValidationUtilities.ValidateWorkbook(configurationWorkbookPath))

    return validationResults


def SetInputsTemplateUittredepunten(configurationBookPath, outputTemplateUittredepunten):

    #   Validate inputs

    validationResults = ValidateInputsTemplate(configurationBookPath)

    #   Check if inputs are valid
    if len(filter(lambda v: v[0] == False, validationResults)) > 0:
        for validationResult in validationResults:
            arcpy.AddError(validationResult[1])
            return False

    VulUittredePunten.UpdateConfigurationBook(configurationBookPath)
    InputConfig.templatePathUittredepunten = outputTemplateUittredepunten



def MaakUittredepuntenTemplate(configurationWorkbookPath, outputFeatureclass):
    #   Read kolomdefinities from workbook

    SetInputsTemplateUittredepunten(configurationWorkbookPath, outputFeatureclass)

    definitionWorksheetUittredepuntenInputs = InputConfig.definitionWorksheetUittredepuntenInputs

    definitionWorkbookUittredepuntenInput = os.path.split(definitionWorksheetUittredepuntenInputs)[0]
    definitionSheetNameUittredepuntenInput = os.path.split(definitionWorksheetUittredepuntenInputs)[1].replace("$", "")

    kolomDefinitiesUittredePunten = CalculationFileUtilities.LeesKolomDefinitiesVoorTemplateXlrd(
        definitionWorkbookUittredepuntenInput, definitionSheetNameUittredepuntenInput, "Uittredepunten", isInput=True)

    outputGdb = os.path.split(outputFeatureclass)[0]
    tableName = os.path.split(outputFeatureclass)[1]

    CreateTemplates.MaakTabel(outputGdb,tableName,kolomDefinitiesUittredePunten)
