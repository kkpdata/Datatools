import os
import arcpy

def GenereerBuffers(outputUittredepuntenAggregatie, outputBufferFeatureclass, veldnaamBufferAfstand):
    arcpy.AddMessage("Aanmaken buffers benodigde kwelweglengte op basis van veld {0} in feature class {1}".format(veldnaamBufferAfstand,outputUittredepuntenAggregatie))
    arcpy.Buffer_analysis(outputUittredepuntenAggregatie, outputBufferFeatureclass, buffer_distance_or_field=veldnaamBufferAfstand, dissolve_option="ALL")
