# Mock do arcpy para desenvolvimento sem ArcGIS
# Substitui funcionalidades básicas para evitar erros de importação

class MockArcPy:
    def __init__(self):
        self.env = MockEnv()
        self.da = MockDA()
        self.management = MockManagement()
    
    def SetLogHistory(self, value):
        pass
    
    def Exists(self, path):
        return False
    
    def Delete_management(self, path):
        pass
    
    def CreateTable_management(self, *args):
        pass
    
    def CopyFeatures_management(self, *args):
        pass
    
    def Select_analysis(self, *args):
        pass
    
    def Intersect_analysis(self, *args):
        pass
    
    def AddField_management(self, *args):
        pass
    
    def CalculateField_management(self, *args):
        pass
    
    def Dissolve_management(self, *args):
        pass

class MockEnv:
    def __init__(self):
        self.overwriteOutput = True
        self.autoCommit = ""
        self.workspace = ""
        self.scratchWorkspace = "in_memory"

class MockDA:
    def SearchCursor(self, *args, **kwargs):
        return MockCursor()
    
    def UpdateCursor(self, *args, **kwargs):
        return MockCursor()
    
    def InsertCursor(self, *args, **kwargs):
        return MockCursor()

class MockManagement:
    def Delete(self, path):
        pass
    
    def CopyFeatures(self, *args):
        pass
    
    def DeleteFeatures(self, path):
        pass
    
    def Append(self, *args):
        pass

class MockCursor:
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass
    
    def insertRow(self, row):
        pass
    
    def deleteRow(self):
        pass
    
    def reset(self):
        pass
    
    def __iter__(self):
        return iter([])

# Instância global
arcpy = MockArcPy()
