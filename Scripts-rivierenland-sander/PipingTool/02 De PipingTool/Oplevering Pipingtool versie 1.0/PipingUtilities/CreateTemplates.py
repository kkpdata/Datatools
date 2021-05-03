import os
import arcpy

spatialReference = arcpy.SpatialReference("RD New")

def MaakTabel(outputGdb, tabelNaam, kolomDefinities, geometryType = "POINT", isStandAlone = False):

    tabelPath = outputGdb + os.sep + tabelNaam

    if (arcpy.Exists(tabelPath)):
        arcpy.AddMessage("Verwijderen bestaande tabel {0}".format(tabelPath))
        arcpy.Delete_management(tabelPath)

    arcpy.AddMessage("Aanmaken tabel {0}".format(tabelPath))

    if isStandAlone == False:
        arcpy.CreateFeatureclass_management(outputGdb,tabelNaam,geometry_type=geometryType,spatial_reference=spatialReference)
    else:
        arcpy.CreateTable_management(outputGdb, tabelNaam)

    #   Loop over kolomDefinities and add fields

    for kolomDefinitie in kolomDefinities:
        arcpy.AddMessage("Adding field {0} to table {1}".format(kolomDefinitie.FieldName,tabelPath))
        if kolomDefinitie.FieldName.lower() != "shape":
            arcpy.AddField_management(tabelPath, kolomDefinitie.FieldName,kolomDefinitie.FieldType,field_alias=kolomDefinitie.Alias)

