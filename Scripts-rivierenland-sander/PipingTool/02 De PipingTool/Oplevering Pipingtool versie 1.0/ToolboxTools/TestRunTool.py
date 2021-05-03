import os
import arcpy

from PipingUtilities import ValidationUtilities
from TestScripts import RunPipingBerekening

class TestRunTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "0 - Voer testrun uit"
        self.description = "Stap 0 Voer een testrun uit en valideer de uitkomsten"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        #   Parameter 0
        testDataRootfolder = arcpy.Parameter(
            displayName="Map met test data",
            name="testDataRootfolder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        params = [testDataRootfolder]

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

        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        testdataRoot = parameters[0].valueAsText
        RunPipingBerekening.RunAutomatedTest(testdataRootfolder=testdataRoot)
        testSuccesfull, errorMessages = ValidationUtilities.ValideerTestresultaten(testdataRootfolder=testdataRoot)

        if len(errorMessages) > 0:
            arcpy.AddMessage("Er zijn fout opgetreden bij het runnen en valideren van de testset:")

            for errorMessage in errorMessages:
                arcpy.AddError(errorMessage)
        else:
            arcpy.AddMessage("De test is succesvol doorlopen.")

        return
