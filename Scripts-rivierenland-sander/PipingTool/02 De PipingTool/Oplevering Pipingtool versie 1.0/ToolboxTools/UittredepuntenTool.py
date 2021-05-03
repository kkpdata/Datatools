import arcpy
import os
from TestScripts import VulUittredePunten

class UittredepuntenTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "1b - Vul uittredepunten"
        self.description = "Stap 1b - Invullen attributen uittredepunten vanuit geografische inputs"
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
        uittredepuntenLocaties = arcpy.Parameter(
            displayName="Locaties uittredepunten (punten featureclass)",
            name="uittredepuntenLocaties",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")

        #   Parameter 2
        outputUittredepuntenFeatureclass = arcpy.Parameter(
            displayName="Output feature class uittredepunten",
            name="outputUittredepuntenFeatureclass",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output")

        params = [configuratieTabelPath, uittredepuntenLocaties, outputUittredepuntenFeatureclass]

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
                parameters[0].setErrorMessage("Bestand bestaat niet!")

        if parameters[1].valueAsText and arcpy.Exists(parameters[1].valueAsText):
            description = arcpy.Describe(parameters[1].valueAsText)
            try:
                if description.shapeType != "Point":
                    parameters[1].setErrorMessage("Selecteer een punten featureclass a.u.b..")
            except AttributeError:
                parameters[1].setErrorMessage("Datatype wordt niet ondersteund.")

        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        configuratieTabel = parameters[0].valueAsText
        locatiesUittredepunten = parameters[1].valueAsText
        outputUittredepunten = parameters[2].valueAsText

        VulUittredePunten.SetInputsVulUittredepunten(configuratieTabel, locatiesUittredepunten, outputUittredepunten)
        VulUittredePunten.RunVulUittredepunten()

        return

