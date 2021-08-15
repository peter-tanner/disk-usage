import shutil
from datetime import datetime, date, timedelta
from utils import nextWeek
import os

class Drive:
    def __init__(self, drivePath) -> None:
        self.__drivePath = drivePath
        try:
            self.total, self.used, self.free = shutil.disk_usage(self.__drivePath)
        except:
            self.total = self.used = self.free = ""
        pass

    def toKV_used(self):
        return {self.__drivePath : self.used}
    def toKV_total(self):
        return {self.__drivePath : self.total}
    def toKV_free(self):
        return {self.__drivePath : self.free}

    @staticmethod
    def getDrives(mountPath):
        drives = []
        for drive in os.listdir(mountPath):
            path = Drive.__normalizeDirPath(mountPath+drive)
            drives.append(Drive(path))
        return drives

    @staticmethod
    def getUsed(mountPath):
        __now = datetime.now().isoformat(sep="_")
        row = {
            "time" : __now,
            "next_week" : nextWeek().isoformat()
        }
        for drive in Drive.getDrives(mountPath):
            row.update(drive.toKV_used())
        return row

    @staticmethod
    def getMaxTotal(mountPath):
        drives = Drive.getDrives(mountPath)
        return max(drives, key = lambda d : d.total).total
        

    @staticmethod    
    def __normalizeDirPath(dirPath):
        if dirPath[-1] == '/':
            return dirPath
        return dirPath+'/'

