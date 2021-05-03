import arcpy
import os
import InputConfig
from PipingClasses import PipingCalculationClasses
from PipingUtilities import CalculationFileUtilities, PipingGeoprocessingUtilities
from PipingUtilities import PipingCalculationSettingUtilities
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

def SetBerekeningInputs(configurationWorkbookPath, featureclassUittredepunten, outputGdb, featureclassNameUittredenPuntenPerScenario, featureclassNameUittredePuntenAggregatie):
    validationResults = ValidateInputs(configurationWorkbookPath,featureclassUittredepunten)

    #   Check if inputs are valid
    if len(filter(lambda v: v[0] == False,validationResults)) > 0:
        for validationResult in validationResults:
            arcpy.AddError(validationResult[1])
            return False

    scriptingRootFolder = os.path.split(os.path.dirname(__file__))[0]
    configurationBookInternal = scriptingRootFolder + r"\Configuratietabel\ConfiguratieInputsOutputs.xlsm"

    UpdateConfigurationBook(configurationWorkbookPath)
    UpdateConfigurationBookInternal(configurationBookInternal)

    InputConfig.outputGdbVoorUittredepunten = os.path.split(featureclassUittredepunten)[0]
    InputConfig.naamFeatureclassUittredenpunten = os.path.split(featureclassUittredepunten)[1]
    InputConfig.outputGdbPipingBerekening = outputGdb
    InputConfig.featureclassNameUittredenPuntenPerScenario = featureclassNameUittredenPuntenPerScenario
    InputConfig.featureclassNameUittredePuntenAggregatie = featureclassNameUittredePuntenAggregatie


    return True

def ValidateInputs(configurationWorkbookPath,featureclassUittredepunten):
    validationResults = []

    validationResults.append(ValidationUtilities.ValidateWorkbook(configurationWorkbookPath))
    validationResults.append(ValidationUtilities.ValidateFeatureclass(featureclassUittredepunten,"Point"))

    return validationResults

def StartPipingBerekening():

    internalTabelPath = InputConfig.configuratieTabelInternal

    arcpy.env.overwriteOutput = True
    spatialReference = arcpy.SpatialReference("RD New")

    definitionWorksheetUittredepuntenInput = InputConfig.definitionWorksheetUittredepuntenInputs
    definitionWorksheetOndergrondscenarioInput = InputConfig.definitionWorksheetOndergrondscenarioInputs

    definitionWorksheetOutputs = InputConfig.definitionWorksheetOutputs

    definitionWorkbookOutputs = os.path.split(definitionWorksheetOutputs)[0]
    definitionSheetNameOutput = os.path.split(definitionWorksheetOutputs)[1].replace("$", "")

    tablePathOndergrondScenarios = InputConfig.tablePathOndergrondScenarios

    tablePathUittredepunten = InputConfig.outputGdbVoorUittredepunten + os.sep + InputConfig.naamFeatureclassUittredenpunten

    tableTypeNameUittredepunten = InputConfig.tableTypeNameUittredepunten
    tableTypeNameOndergrondScenarions = InputConfig.tableTypeNameOndergrondScenarions

    outputFeatureclassNameScenarios = InputConfig.featureclassNameUittredenPuntenPerScenario
    outputFeatureclassNameAggregatie = InputConfig.featureclassNameUittredePuntenAggregatie

    outputGdb = InputConfig.outputGdbPipingBerekening

    #   Bijwerken rekeninstellingen op basis van named ranges in configuratietabel

    PipingCalculationSettingUtilities.UpdateCalculationSettings(InputConfig.configuratieTabel)

    if not arcpy.Exists(outputGdb):
        arcpy.AddMessage("Aanmaken geodatabase {0}".format(outputGdb))
        pathSplit = os.path.split(outputGdb)
        arcpy.CreateFileGDB_management(pathSplit[0], pathSplit[1])

    # kolomDefinitiesUittredePunten = CalculationFileUtilities.LeesKolomDefinitiesVoorTemplateXlrd( definitionWorkbookUittredepuntenInput, definitionSheetNameUittredepuntenInput, "Uittredepunten", isInput=True)
    # inputKolommenAggregatie = CalculationFileUtilities.LeesKolomDefinitiesVoorTemplateXlrd(definitionWorkbookOutputs, definitionSheetNameOutput, "ResultaatPipingCategorie", isInput=True)
    outputKolommenAggregatie = CalculationFileUtilities.LeesKolomDefinitiesVoorTemplateXlrd(definitionWorkbookOutputs,
                                                                                            definitionSheetNameOutput,
                                                                                            "ResultaatPipingCategorie",
                                                                                            isInput=False)

    outputPutTableBerekeningen = outputGdb + os.sep + outputFeatureclassNameScenarios
    outputTableAggregatiePerPunt = outputGdb + os.sep + outputFeatureclassNameAggregatie

    uittredepuntenTabel = CalculationFileUtilities.LeesBestandIn(tableTypeNameUittredepunten, "UittredepuntenID",
                                                                 tablePathUittredepunten,
                                                                 definitionWorksheetUittredepuntenInput,
                                                                 definitionWorksheetOutputs,
                                                                 onlyRequiredParameters=True)
    ondergrondTabel = CalculationFileUtilities.LeesBestandIn(tableTypeNameOndergrondScenarions,
                                                             "OndergrondscenarioID [-]", tablePathOndergrondScenarios,
                                                             definitionWorksheetOndergrondscenarioInput,
                                                             definitionWorksheetOutputs, onlyRequiredParameters=True)

    #   Read scenario names from Excel

    scenarioNamesDict = dict()

    for scenarioIndex in range(1, 7):
        scenarioRangeName = "Scenario{0}".format(scenarioIndex)
        scenarioName = \
            PipingCalculationSettingUtilities.GetNamedRangeValueSingle(InputConfig.configuratieTabel,
                                                                       scenarioRangeName)[2]
        scenarioNamesDict[scenarioIndex] = scenarioName

    uittredepunten = []
    for puntID in uittredepuntenTabel.TabelRijenDict.keys():
        uittredepunt = PipingCalculationClasses.Uittredepunt(puntID, uittredepuntenTabel.TabelRijenDict[puntID],
                                                             scenarioNamesDict)
        uittredepunten.append(uittredepunt)

    ondergrondscenarios = []

    for scenarioID in ondergrondTabel.TabelRijenDict.keys():
        ondergrondScenario = PipingCalculationClasses.OndergrondScenario(scenarioID,
                                                                         ondergrondTabel.TabelRijenDict[scenarioID])
        ondergrondscenarios.append(ondergrondScenario)

    #   Maak PipingCalculationScenario objecten aan (combinatie van een uittredepunt en een ondergrondscenario)

    pipingCalculationScenarios = []

    errorsScenarioKansen = []

    for uittredepunt in uittredepunten:
        #   Filter ondergrondscenarios op basis van vakID

        #arcpy.AddMessage("Berekening voor {0}".format(uittredepunt.UittredepuntID))

        #   Moet nog een check toegevoegd worden of de som van de lokale kansen optelt tot 1
        scenariosVoorPunt = list(filter(lambda s: s.Vaknaam == uittredepunt.Vaknaam, ondergrondscenarios))

        totaleKans = 0

        for scenarioVoorPunt in scenariosVoorPunt:

            pipingCalculationScenario = PipingCalculationClasses.PipingCalculationScenario(uittredepunt,
                                                                                           scenarioVoorPunt)
            pipingCalculationScenario.BepaalLokaleKans()
            totaleKans += pipingCalculationScenario.LokaleKans

            #   Run berekening alleen als het ondergrondscenario van toepassing is

            if pipingCalculationScenario.LokaleKans > 0:
                pipingCalculationScenario.RunBerekening()
                pipingCalculationScenarios.append(pipingCalculationScenario)


        diffKans = totaleKans - float(1)

        if diffKans > 0.0001:
            errorsScenarioKansen.append("De opgetelde scenariokansen voor zijn niet gelijk aan 1 voor uittredepunt {0}; som is {1}".format(uittredepunt.UittredepuntID, totaleKans))

    if len(errorsScenarioKansen) > 0:
        for errorMessage in errorsScenarioKansen:
            arcpy.AddWarning(errorMessage)

        arcpy.AddError("Berekening is onderbroken vanwege fouten in de scenariokansen")
        return False

    #   First delete existing output

    if arcpy.Exists(outputPutTableBerekeningen):
        arcpy.Delete_management(outputPutTableBerekeningen)

    CalculationFileUtilities.MergeUittredepuntenEnOndergrondScenarios(outputPutTableBerekeningen, uittredepuntenTabel,
                                                                      ondergrondTabel, pipingCalculationScenarios,
                                                                      spatialReference=spatialReference)

    #   Groepeer op UittredepuntID

    pipingCalculationAggregaties = []

    for uittredepunt in uittredepunten:
        #   Filter pipingCalculationScenarios by ID

        pipingCalculationScenariosSelection = filter(lambda p: p.UittredepuntID == uittredepunt.UittredepuntID,
                                                     pipingCalculationScenarios)

        pipingCalculationResultaat = PipingCalculationClasses.PipingCalculationResultaat(uittredepunt,
                                                                                         pipingCalculationScenariosSelection)
        pipingCalculationResultaat.AggregeerResultaten()
        pipingCalculationAggregaties.append(pipingCalculationResultaat)

    #   First delete existing output

    if arcpy.Exists(outputTableAggregatiePerPunt):
        arcpy.Delete_management(outputTableAggregatiePerPunt)

    CalculationFileUtilities.GenereerAggregatie(outputTableAggregatiePerPunt, outputKolommenAggregatie,
                                                pipingCalculationAggregaties, spatialReference)

    #   Genereer buffers met kritieke pijplengte (vanuit punten per scenario)
    #   Via de 'Dissolve all' optie wordt het maximum van de kritieke pijplengtes gegenereerd

    outputBuffersKritiekePipelengte = InputConfig.outputGdbPipingBerekening + os.sep + InputConfig.featureclassNameKritiekePipelengteBuffers
    PipingGeoprocessingUtilities.GenereerBuffers(outputPutTableBerekeningen, outputBuffersKritiekePipelengte,
                                                 "KritiekePipelengte")

    #   Genereer buffers met maatgevende benodigde kwelweglengte (vanuit geaggregeerde punten)

    outputBuffersMaxEffectieveKwelweglengte = InputConfig.outputGdbPipingBerekening + os.sep + InputConfig.featureclassNameMaxKwelweglengteBuffers
    outputBuffersMaatgevendeBenodigdeKwelweglengte = InputConfig.outputGdbPipingBerekening + os.sep + InputConfig.featureclassNameBenodigdeKwelweglengteBuffers

    PipingGeoprocessingUtilities.GenereerBuffers(outputTableAggregatiePerPunt, outputBuffersMaxEffectieveKwelweglengte,
                                                 "MaximaleEffectieveKwelweglengte")
    PipingGeoprocessingUtilities.GenereerBuffers(outputTableAggregatiePerPunt,
                                                 outputBuffersMaatgevendeBenodigdeKwelweglengte,
                                                 "MaxBenodigdeKwelweglengte")

    return True
    arcpy.AddMessage("Ready")



def RunAutomatedTest(testdataRootfolder = None):
    print(__file__)

    #   Get root folder for scripting
    if testdataRootfolder == None:
        testscriptFolder = os.path.split(__file__)[0]
        testdataRootfolder = os.path.split(testscriptFolder)[0] + os.sep + "Testdata"

    configuratietabel = testdataRootfolder + os.sep + "Configuratietabel_test.xlsm"
    uittredepunten = testdataRootfolder + r"\Uittredepunten.gdb\uittredepunten"
    outputGdb = testdataRootfolder + os.sep + "Output.gdb"

    featureclassNameUittredenPuntenPerScenario = "OutputPipingCalculationScenarios"
    featureclassNameUittredePuntenAggregatie = "OutputAggregatiePerUittredepunt"

    SetBerekeningInputs(configuratietabel, uittredepunten, outputGdb, featureclassNameUittredenPuntenPerScenario, featureclassNameUittredePuntenAggregatie)
    StartPipingBerekening()

    print(testdataRootfolder)

    return
