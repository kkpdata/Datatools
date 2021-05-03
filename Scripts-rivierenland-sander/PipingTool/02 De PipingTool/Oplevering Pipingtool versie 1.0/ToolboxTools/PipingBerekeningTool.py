import arcpy
import os
from TestScripts import RunPipingBerekening

class PipingBerekeningTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "2 - Uitvoeren piping berekening"
        self.description = "Stap 2 - Uitvoeren piping berekening voor uittredepunten feature class met ingevulde attributen"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        #   Parameter 0
        configuratieTabelPath = arcpy.Parameter(
            displayName="Configuratietabel (Excel)",
            name="configuratieTabelPath",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")

        #   Parameter 1
        uittredepuntenFeatureclass = arcpy.Parameter(
            displayName="Uittredepunten featureclass)",
            name="uittredepuntenFeatureclass",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")

        #   Parameter 2
        outputGdb = arcpy.Parameter(
            displayName="Output geodatabase",
            name="outputGdb",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        #   Parameter 3
        scenarioFeatureclassName = arcpy.Parameter(
            displayName="Naam feature class resultaten per scenario",
            name="scenarioFeatureclassName",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        #   Parameter 4
        aggregatieFeatureclassName = arcpy.Parameter(
            displayName="Naam feature class resultaten aggregaties",
            name="aggregatieFeatureclassName",
            datatype="GPString",
            parameterType="Required",
            direction="Input")



        params = [configuratieTabelPath, uittredepuntenFeatureclass, outputGdb, scenarioFeatureclassName, aggregatieFeatureclassName]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""

        # Check if parameter 0 (configuratietabel) has file extension *.xlsx
        if parameters[0].valueAsText and parameters[0].valueAsText != "":
            if arcpy.Exists(parameters[0].valueAsText):
                description = parameters[0].valueAsText
                extension = os.path.splitext(description)[1]
                if extension != ".xlsx" and extension != ".xlsm":  # and extension != ".xls"
                    parameters[0].setErrorMessage("Selecteer een *.xlsx- of *.xlsm-bestand a.u.b.")
            else:
                parameters[0].setErrorMessage("Data does not exist!")

        if parameters[1].valueAsText and arcpy.Exists(parameters[1].valueAsText):
            description = arcpy.Describe(parameters[1].valueAsText)
            try:
                if description.shapeType != "Point":
                    parameters[1].setErrorMessage("Selecteer een punten featureclass a.u.b..")
            except AttributeError:
                parameters[1].setErrorMessage("Datatype not supported")

        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        configuratietabel = parameters[0].valueAsText
        featureclassUittredepunten = parameters[1].valueAsText
        outputGdb = parameters[2].valueAsText
        featureclassNameUittredenPuntenPerScenario = parameters[3].valueAsText
        featureclassNameUittredePuntenAggregatie = parameters[4].valueAsText

        RunPipingBerekening.SetBerekeningInputs(configuratietabel, featureclassUittredepunten, outputGdb, featureclassNameUittredenPuntenPerScenario,
                            featureclassNameUittredePuntenAggregatie)
        calculationSucceeded = RunPipingBerekening.StartPipingBerekening()

        if calculationSucceeded:
            arcpy.AddMessage("Berekening is succesvol afgerond")
        else:
            arcpy.AddError("Berekening is onderbroken")

        return
