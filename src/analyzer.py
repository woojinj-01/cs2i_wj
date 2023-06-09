"""
Author: Woojin Jung (GitHub: woojinj-01)
Email: blankspace@kaist.ac.kr

"""
import os
import error
import cleaner
import institution
import util

"""
class Analyzer

Analyzing method added. 
This class encapsulates cleaners over different fields.


"""
class Analyzer:

    #instIdDict = {}
    #instDict = {}

    @error.callStackRoutine
    def __init__(self):

        self.__cleanerDict = {}
        self.instIdDict = {}
        self.instDict = {}

        self.__cleanedFlag = 0

    @error.callStackRoutine
    def __raiseCleanedFlag(self):
        self.__cleanedFlag = 1
    
    @error.callStackRoutine
    def __ifCleanedFlagNotRaised(self):
        return int(0 == self.__cleanedFlag)
        
    @error.callStackRoutine
    def __queryInstDictById(self, argInstId):

        return int(argInstId in self.instDict)
    
    @error.callStackRoutine
    def getInstitution(self, argInstInfo: institution.InstInfo, argField: str) -> institution.Institution:

        if(0 == self.__queryInstDictById(argInstInfo.instId)):
            self.instDict[argInstInfo.instId] = institution.Institution(argInstInfo)
            error.LOGGER.report("Got New Institution", error.LogType.INFO)

        self.instDict[argInstInfo.instId].getField(argField)
        
        return self.instDict[argInstInfo.instId]
    
    @error.callStackRoutine
    def getExistingInstitution(self, argInstId) -> institution.Institution:

        if(0 == self.__queryInstDictById(argInstId)):
            error.LOGGER.report("Invalid Institution ID", error.LogType.WARNING)
            return None
        
        return self.instDict[argInstId]
    
    @error.callStackRoutine
    def getInstDict(self):
        return self.instDict
    
    
    @error.callStackRoutine
    def printAllInstitutions(self):

        for item in sorted(self.instDict.items()):
            print(type(item[1]))
            item[1].printInfo()
    
    @error.callStackRoutine
    def __queryCleanerDict(self, argField):

        return int(argField in self.__cleanerDict)

    @error.callStackRoutine
    def getCleanerFor(self, argField):

        if(util.isEmptyData(argField)):
            error.LOGGER.report("Attempt to generate Cleaner with empty value is suppressed",error.LogType.INFO)
            return None

        if(0 == self.__queryCleanerDict(argField)):
            self.__cleanerDict[argField] = cleaner.Cleaner(self, argField)
            error.LOGGER.report("Got New Cleaner", error.LogType.INFO)
        
        return self.__cleanerDict[argField]

    @error.callStackRoutine
    def getInstIdFor(self, argInstInfo: institution.InstInfo):

        keyTuple = argInstInfo.returnKeyTuple()

        if(keyTuple in self.instIdDict):
            return self.instIdDict[keyTuple]
        else:
            newId = len(self.instIdDict)+1
            self.instIdDict[keyTuple] = newId
            error.LOGGER.report("New Inst ID Allocated", error.LogType.INFO)

            return newId
    
    @error.callStackRoutine
    def getInstIdForInit(self, argKeyTuple: tuple):

        if(argKeyTuple in self.instIdDict):
            return 0
        else:
            newId = len(self.instIdDict)+1
            self.instIdDict[argKeyTuple] = newId

            return 1

    @error.callStackRoutine
    def printInstIdDict(self):

        print(self.instIdDict)

    @error.callStackRoutine
    def loadInstIdDictFrom(self, argFilePath):
        
        instIdDf = util.readFileFor(argFilePath, [util.FileExt.XLSX, util.FileExt.CSV])

        if(instIdDf.empty):
            error.LOGGER.report("Failed to Initialize InstID Dictionary", error.LogType.WARNING)
            return 0
        
        returnValue = 1

        for numRow in range(len(instIdDf.index)):
            returnValue &= self.getInstIdForInit((instIdDf.iloc[numRow][0], instIdDf.iloc[numRow][1], instIdDf.iloc[numRow][2]))

        if(0 == returnValue):
            error.LOGGER.report("Failed to Initialize InstID Dictionary", error.LogType.WARNING)
        return returnValue
    
    @error.callStackRoutine
    def __cleanDataForFile(self, argFilePath):

        targetDf = util.readFileFor(argFilePath, [util.FileExt.XLSX, util.FileExt.CSV])
        rowIterator = util.rowIterator(targetDf.columns,'Degree')

        targetRow = None
        field = None

        for numRow in range(len(targetDf.index)):

            targetRow = targetDf.iloc[numRow]
            field = targetRow[rowIterator.findFirstIndex('Department', 'APPROX')]

            cleaner = self.getCleanerFor(field)

            if(None != cleaner):
                cleaner.cleanRow(targetRow, rowIterator)

        error.LOGGER.report(" ".join([argFilePath, "is Cleaned"]), error.LogType.INFO)

    @error.callStackRoutine
    def cleanData(self):

        error.LOGGER.report("Start Cleaning Data", error.LogType.INFO)

        targetDir = '../dataset/dirty'

        if(False == os.path.isdir(targetDir)):
            error.LOGGER.report(" ".join(["No Directory Named", targetDir]), error.LogType.CRITICAL)

        for fileName in os.listdir(targetDir):
            if('~$' == fileName[0:2]):  #getting rid of cache file
                continue

            if('.xlsx' == os.path.splitext(fileName)[1]):
                self.__cleanDataForFile(os.path.join(targetDir, fileName))

        self.__raiseCleanedFlag()

        error.LOGGER.report("Data are Cleaned Now!", error.LogType.INFO)
    
    @error.callStackRoutine
    def exportVertexAndEdgeListFor(self, argField, argFileExtension: util.FileExt):

        if(self.__ifCleanedFlagNotRaised()):
            error.LOGGER.report("Attempt denied. Data are not cleaned yet.", error.LogType.ERROR)

        if(0 == self.__queryCleanerDict(argField)):
            error.LOGGER.report("Invalid Field Name", error.LogType.ERROR)
            return 0
        
        self.__cleanerDict[argField].exportVertexAndEdgeListAs(argFileExtension)

        return 1

    @error.callStackRoutine
    def exportVertexAndEdgeListForAll(self, argFileExtension: util.FileExt):

        if(self.__ifCleanedFlagNotRaised()):
            error.LOGGER.report("Attempt denied. Data are not cleaned yet.", error.LogType.ERROR)
            return 0

        error.LOGGER.report(" ".join(["Exporting All Fields as", util.fileExtToStr(argFileExtension)]), error.LogType.INFO)

        for cleaner in util.getValuesListFromDict(self.__cleanerDict):

            if(str == type(cleaner.field)):
                cleaner.exportVertexAndEdgeListAs(argFileExtension)

        error.LOGGER.report(" ".join(["Exported All Fields as", util.fileExtToStr(argFileExtension)]), error.LogType.INFO)
        return 1
    
    @error.callStackRoutine
    def calcGiniCoeffFor(self, argField):

        if(self.__ifCleanedFlagNotRaised()):
            error.LOGGER.report("Attempt denied. Data are not cleaned yet.", error.LogType.ERROR)
            return 0

        if(0 == self.__queryCleanerDict(argField)):
            error.LOGGER.report("Invalid Field Name", error.LogType.ERROR)
            return 0

        return self.__cleanerDict[argField].calcGiniCoeff()
    
    @error.callStackRoutine
    def calcGiniCoeffForAll(self):

        if(self.__ifCleanedFlagNotRaised()):
            error.LOGGER.report("Attempt denied. Data are not cleaned yet.", error.LogType.ERROR)
            return dict()
        
        error.LOGGER.report("Calculating Gini Coefficient for All Fields", error.LogType.INFO)

        giniCoeffDict = {}

        for field in util.getKeyListFromDict(self.__cleanerDict):
            giniCoeffDict[field] = self.calcGiniCoeffFor(field)

        error.LOGGER.report("Sucesssfully Calculated Gini Coefficient for All Fields!", error.LogType.INFO)
        return giniCoeffDict
    
    @error.callStackRoutine
    def calcMVRRAnkFor(self, argField):
        if(type(argField) != str):
            error.LOGGER.report("Field name should be a string", error.LogType.ERROR)
            return 0

        if(self.__ifCleanedFlagNotRaised()):
            error.LOGGER.report("Attempt denied. Data are not cleaned yet.", error.LogType.ERROR)
            return 0
        
        if(0 == self.__queryCleanerDict(argField)):
            error.LOGGER.report("Invalid Field Name", error.LogType.ERROR)
            return 0
        
        error.LOGGER.report(' '.join(["Calculating MVR Rank for", argField]), error.LogType.INFO)

        return self.__cleanerDict[argField].calcMVRRank()
    
    @error.callStackRoutine
    def calcMVRRAnkForAll(self):

        if(self.__ifCleanedFlagNotRaised()):
            error.LOGGER.report("Attempt denied. Data are not cleaned yet.", error.LogType.ERROR)
            return 0
        
        error.LOGGER.report("Calculating MVR Ranks for All Fields", error.LogType.INFO)

        returnValue = 1

        for field in util.getKeyListFromDict(self.__cleanerDict):
            returnValue = returnValue and self.calcMVRRAnkFor(field)

        error.LOGGER.report("Sucesssfully Calculated MVR Ranks for All Fields!", error.LogType.INFO)

        return returnValue
    
    @error.callStackRoutine
    def calcAvgMVRMoveBasedOnGender(self, argGender: util.Gender):

        returnDict = {}

        for cleaner in util.getValuesListFromDict(self.__cleanerDict):
            returnDict[cleaner.field] = cleaner.calcAvgMVRMoveBasedOnGender(argGender)

        return returnDict
    
    @error.callStackRoutine
    def calcAvgMVRMoveBasedOnGenderForField(self, argGender: util.Gender, argField: str):

        if(0 == self.__queryCleanerDict(argField)):
            error.LOGGER.report("Invalid Field.", error.LogType.ERROR)

        returnDict = {}

        returnDict[argField] = self.getCleanerFor(argField).calcAvgMVRMoveBasedOnGender(argGender)

        return returnDict

    @error.callStackRoutine
    def calcAvgMVRMoveForRange(self, argPercentLow: int, argPercentHigh: int):

        returnDict = {}

        for cleaner in util.getValuesListFromDict(self.__cleanerDict):
            returnDict[cleaner.field] = cleaner.calcAvgMVRMoveForRange(argPercentLow, argPercentHigh)

        return returnDict

    @error.callStackRoutine
    def calcAvgMVRMoveForRangeForField(self, argPercentLow: int, argPercentHigh: int, argField: str):

        if(0 == self.__queryCleanerDict(argField)):
            error.LOGGER.report("Invalid Field.", error.LogType.ERROR)

        returnDict = {}

        returnDict[argField] = self.getCleanerFor(argField).calcAvgMVRMoveForRange(argPercentLow, argPercentHigh)

        return returnDict     

if(__name__ == '__main__'):

    error.LOGGER.report("This Module is Not for Main Function", error.LogType.CRITICAL)
