import arcpy
import os
import InputConfig
from PipingUtilities import CalculationFileUtilities, CreateTemplates
from PipingUtilities import UittredePuntenUtilities
from PipingUtilities import ValidationUtilities

def UpdateConfigurationBook(configurationBookPath):
    InputConfig.configuratieTabel = configurationBookPath
    InputConfig.definitionWorksheetUittredepuntenInputs = configurationBookPath + r"\InputsUittredepunten$"
    InputConfig.definitionWorksheetScenarioNames = configurationBookPath + r"\GenererenScenarios"
    InputConfig.tablePathOndergrondScenarios = configurationBookPath + r"\Ondergrondscenarios"

def UpdateConfigurationBookInternal(configurationBookPath):
    InputConfig.configuratieTabelInternal = configurationBookPath
    InputConfig.definitionWorksheetOndergrondscenarioInputs = configurationBookPath + r"\InputsOndergrondscenarios$"
    InputConfig.definitionWorksheetOutputs = configurationBookPath + r"\Outputs$"








def ValidateInputsUittredepunten(configurationWorkbookPath,featureclassUittredepunten):
    validationResults = []

    validationResults.append(ValidationUtilities.ValidateWorkbook(configurationWorkbookPath))
    validationResults.append(ValidationUtilities.ValidateFeatureclass(featureclassUittredepunten,"Point"))

    return validationResults












def SetInputsVulUittredepunten(configurationBookPath, featureclassLocatiesUittredepunten, outputFeatureclassUittredepunten):
    scriptingRootFolder = os.path.split(os.path.dirname(__file__))[0]
    configurationBookInternal = scriptingRootFolder + r"\Configuratietabel\ConfiguratieInputsOutputs.xlsm"

    #   Validate inputs

    validationResults = ValidateInputsUittredepunten(configurationBookPath,featureclassLocatiesUittredepunten)

    #   Check if inputs are valid
    if len(filter(lambda v: v[0] == False, validationResults)) > 0:
        for validationResult in validationResults:
            arcpy.AddError(validationResult[1])
            return False

    UpdateConfigurationBook(configurationBookPath)
    UpdateConfigurationBookInternal(configurationBookInternal)

    InputConfig.basisFeatureClassInput = featureclassLocatiesUittredepunten
    InputConfig.outputGdbVoorUittredepunten = os.path.split(outputFeatureclassUittredepunten)[0]
    InputConfig.naamFeatureclassUittredenpunten = os.path.split(outputFeatureclassUittredepunten)[1]



def RunVulUittredepunten(deleteIntermediateOutputs = False):
    arcpy.env.overwriteOutput = True

    definitionWorksheetUittredepuntenInputs = InputConfig.definitionWorksheetUittredepuntenInputs
    outputGdb = InputConfig.outputGdbVoorUittredepunten
    basisbestandInput = InputConfig.basisFeatureClassInput
    uittredepuntenFeatureclassNaam = InputConfig.naamFeatureclassUittredenpunten



    if not arcpy.Exists(outputGdb):
        pathSplit = os.path.split(outputGdb)
        arcpy.AddMessage("Aanmaken geodatabase {0}".format(outputGdb))
        arcpy.CreateFileGDB_management(pathSplit[0], pathSplit[1])

    #   Maak een nieuwe featureclass op basis van de Excelsheet met kolomdefinities

    arcpy.AddMessage("Uitlezen kolomdefinities uit sheet {0}".format(definitionWorksheetUittredepuntenInputs))

    # kolomDefinitiesUittredePunten = CalculationFileUtilities.LeesKolomDefinitiesVoorTemplate(definitionWorksheetUittredepuntenInputs, "Uittredepunten", isInput=True)

    definitionWorkbookUittredepuntenInput = os.path.split(definitionWorksheetUittredepuntenInputs)[0]
    definitionSheetNameUittredepuntenInput = os.path.split(definitionWorksheetUittredepuntenInputs)[1].replace("$", "")

    kolomDefinitiesUittredePunten = CalculationFileUtilities.LeesKolomDefinitiesVoorTemplateXlrd(
        definitionWorkbookUittredepuntenInput, definitionSheetNameUittredepuntenInput, "Uittredepunten", isInput=True)

    #   Valideer kolomdefinities

    definitiesValid = UittredePuntenUtilities.ValideerKolomdefinities(kolomDefinitiesUittredePunten)

    if not definitiesValid:
        arcpy.AddError("Er is een fout opgetreden bij het vullen van de uittredepunten.")
        return False

    uittredepuntenFeatureclass = outputGdb + os.sep + uittredepuntenFeatureclassNaam

    CreateTemplates.MaakTabel(outputGdb, uittredepuntenFeatureclassNaam, kolomDefinitiesUittredePunten, "POINT")

    #   Kopieer handmatige input

    UittredePuntenUtilities.KopieerGeometrie(basisbestandInput, uittredepuntenFeatureclass)

    #   Maak veld met unieke nummers aan
    UittredePuntenUtilities.VulPuntNummers(uittredepuntenFeatureclass)

    #   Houd lijst met tijdelijke bestanden bij

    intermediateOutputs = []

    #   Vul kolommen die uit rasterdata worden afgeleid

    UittredePuntenUtilities.VulRasterwaardeKolommen(uittredepuntenFeatureclass, kolomDefinitiesUittredePunten, outputGdb, intermediateOutputs)

    #   Vul kolommen op basis van spatial joins
    UittredePuntenUtilities.VulSpatialJoinKolommen(uittredepuntenFeatureclass, kolomDefinitiesUittredePunten, outputGdb, intermediateOutputs)

    #   Vul kolommen waarvoor een specifieke functie gerund moet worden
    UittredePuntenUtilities.VulSpecifiekeKolommen(uittredepuntenFeatureclass, kolomDefinitiesUittredePunten, outputGdb)

    if deleteIntermediateOutputs:
        for intermediateResult in intermediateOutputs:
            arcpy.AddMessage("Delete intermediate result {0}".format(intermediateResult))
            arcpy.Delete_management(intermediateResult)

    arcpy.AddMessage("Ready")
    return True

