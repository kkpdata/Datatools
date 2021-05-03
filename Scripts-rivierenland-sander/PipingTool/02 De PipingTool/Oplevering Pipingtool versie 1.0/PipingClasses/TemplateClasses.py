class KolomDefinitie:
    def __init__(self, fieldName, fieldType, alias, linkType = None, sourceDataset = None, inputFieldName = None, whereClause = None, propertyName = None, columnIndex = -1):
        self.FieldName = fieldName
        self.FieldType = fieldType
        self.Alias = alias
        self.LinkType = linkType
        self.SourceDataset = sourceDataset
        self.InputFieldName = inputFieldName
        self.WhereClause = whereClause
        self.PropertyName = propertyName
        self.ColumnIndex = columnIndex

class TemplateFeatureclass:
    def __init__(self, tabelNaam, geometryType = "POINT", isStandAlone = False):
        self.TabelNaam = tabelNaam
        self.GeometryType = geometryType
        self.IsStandAlone = isStandAlone