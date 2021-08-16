import csv
from copy import copy
from pathlib import Path

class CSVFile:
    def __init__(self, filePath, delimiter=",") -> None:
        self.__rewrite = False
        self.__delimiter = delimiter
        self.__filePath = Path(filePath)
        self.__addBuffer = []
        self.__newFile = self.fileInit()
        self.length = 0
        with open(filePath, "r") as file:
            data = csv.DictReader(file,delimiter=delimiter)
            if data.fieldnames == None:
                self.__fields = list()
                self.__newFile = True
            else:
                self.__fields = list(data.fieldnames)
            self.__data = list(data)
            self.length = len(self.__data)
        pass

    def fileInit(self):
        if not self.__filePath.exists():
            open(self.__filePath,'a').close()
            return True
        return False

    def addRow(self,row):
        print("ROW", row)
        print("ROW", row.keys())
        fields = row.keys()
        for field in fields:
            if not field in self.__fields:
                self.__fields.append(field)
        self.__data.append(row)
        self.__addBuffer.append(row)
        self.length = len(self.__data)

    def getRow(self,rowIdx):
        return self.__data[rowIdx]

    def validate(self):
        if self.__rewrite:
            return False
        alreadyValid = True
        expectedFieldLen = len(self.__fields)
        addIdx = len(self.__data)-len(self.__addBuffer)
        idx = 0
        for row in self.__data:
            fields = row.keys()
            fieldsLen = len(fields)
            if fieldsLen < expectedFieldLen:
                for expectedField in self.__fields:
                    if expectedField not in fields:
                        row.update({expectedField: ""})
                        if idx < addIdx:
                            alreadyValid = False
            elif fieldsLen > expectedFieldLen:
                # Omit invalid data.
                firstField = self.__fields[0]
                commented = "#"+row[firstField]
                row.update({firstField : commented})
                print("Error on line "+str(idx)+" - Omitted from file")
                alreadyValid = False
            idx += 1
        return alreadyValid

    def writeAppend(self,filepath):
        print("Append - no header change")
        with open(filepath, "a", newline="") as file:
            w = csv.DictWriter(file, fieldnames=self.__fields)
            w.writerows(self.__addBuffer)
    def writeFile(self,filepath):
        print("Rewrite - header changed")
        with open(filepath, "w") as file:
            w = csv.DictWriter(file, self.__fields)
            w.writeheader()
            w.writerows(self.__data)
    
    def efficientWriteFile(self):
        filepath = self.__filePath
        if self.validate() and not self.__newFile:
            self.writeAppend(filepath)
        else:
            self.writeFile(filepath)
    
    def search(self,k,v,adjacent=False,backwards=False,start=0):
        results = []
        data = self.__data
        r = range(start,len(data))
        if backwards:
            r = range(start,-len(data)-1,-1)
        for i in r:
            row = self.__data[i]
            if k in row.keys() and row[k] == v:
                results.append(row)
            elif adjacent:
                break
        return results
    
    # matches=-1 ==> infinite replacements
    def replaceByKV(self,k,v,newRow,backwards=False,start=0,matches=1):
        infinite = matches < 0
        data = self.__data
        count = 0
        r = range(start,len(data))
        if backwards:
            r = range(start,-len(data)-1,-1)
        for i in r:
            row = self.__data[i]
            if k in row.keys() and row[k] == v:
                self.__data[i] = newRow
                self.__rewrite = True
                count += 1
                if not infinite and count >= matches:
                    return True
        if infinite:
            return count > 0
        return False
    
    def fill(self, row, fillV=0, updateKVs=[]):
        row = copy(row)
        for k in row:
            row[k] = fillV
        for kv in updateKVs:
            row.update(kv)
        self.addRow(row)