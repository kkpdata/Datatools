


#   Rootfolder en configuratietabel zijn van toepassing op script 1 en 2

rootFolderInputProcessing = ""
configuratieTabel = ""
configuratieTabelInternal = ""

#   Script 0: aanmaken template uittredepunten

templatePathUittredepunten = ""

#   Script 1: vullen uittredepunten feature class

basisFeatureClassInput = ""
outputGdbVoorUittredepunten = ""
naamFeatureclassUittredenpunten = "Uittredepunten"

#   Script 2: runnen pipingberekening

definitionWorksheetUittredepuntenInputs = configuratieTabel + r"\InputsUittredepunten$"
definitionWorksheetScenarioNames = configuratieTabel + r"\GenererenScenarios"
definitionWorksheetOndergrondscenarioInputs = configuratieTabelInternal + r"\InputsOndergrondscenarios$"
definitionWorksheetOutputs = configuratieTabelInternal + r"\Outputs$"

tablePathOndergrondScenarios = configuratieTabel + r"\Ondergrondscenarios"
outputGdbPipingBerekening = ""

#   Namen van tabellen in kolom A van definitionWorksheetBerekening (voor het ophalen van de kolomdefinities van de input en output

tableTypeNameUittredepunten = "Uittredepunten"
tableTypeNameOndergrondScenarions = "Ondergrondscenario"

#   Namen van feature classes die in outputGdb gegenereerd worden

featureclassNameUittredenPuntenPerScenario = "OutputPipingCalculationScenarios"
featureclassNameUittredePuntenAggregatie = "OutputAggregatiePerUittredepunt"

featureclassNameKritiekePipelengteBuffers = "OutputBufferKritiekePipelengte"
featureclassNameMaxKwelweglengteBuffers = "OutputBufferMaxEffectieveKwelweglengte"
featureclassNameBenodigdeKwelweglengteBuffers = "OutputBufferMaxBenodigdeKwelweglengte"




