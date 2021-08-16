import sys
import os
import shutil
import csv
import datetime
from drive import Drive
from csvfile import CSVFile
from pathlib import Path
from utils import subtract, nextWeek, sumKV
from datetime import timedelta

SEARCH_PATH = "/mnt/"

class DiskUsage:
    # I probably should be using a database instead of CSV.
    def __init__(self, basepath) -> None:
        basepath = Path(basepath)
        self.SIZE_FILE = basepath.joinpath("size_daily.csv")
        self.DIFF_FILE = basepath.joinpath("diff_daily.csv")
        self.WEEKLY_SIZE_FILE = basepath.joinpath("size_weekly.csv")
        self.WEEKLY_DIFF_FILE = basepath.joinpath("diff_weekly.csv")
        pass

    @staticmethod
    def __daily2weeklyRow(row_):
        row = row_.copy()
        row["time"] = row["next_week"]
        row.pop("next_week")
        return row

    @staticmethod
    def __update_weekly_data(csvfile, updatedRow, previousNextWeek, nextWeek, 
                             makeEmpty=False, duplicateEmpty=0, updateLast=False):
        if csvfile.length < 1:
            if makeEmpty:
                csvfile.fill(updatedRow,updateKVs=[{ "time" : (nextWeek + timedelta(days=-7)).isoformat() }])
            for i in range(0,duplicateEmpty):
                csvfile.addRow(updatedRow)
            csvfile.addRow(updatedRow)
        elif previousNextWeek == nextWeek.isoformat():
            csvfile.replaceByKV("time", nextWeek.isoformat(), updatedRow, backwards=True, start=-1)
        else:
            csvfile.addRow(updatedRow)
            previousWeeklyRow = updatedRow.copy()
            previousWeeklyRow.update({ "time" : previousNextWeek })
            if updateLast:
                csvfile.replaceByKV("time", previousNextWeek, previousWeeklyRow, backwards=True, start=-1)
        csvfile.efficientWriteFile()


    def update(self):
        nextWeek_ = nextWeek()

        sizeDaily = CSVFile(self.SIZE_FILE)
        currentlyUsed = Drive.getUsed(SEARCH_PATH)
        sizeDaily.addRow(currentlyUsed)
        sizeDaily.efficientWriteFile()
        if sizeDaily.length < 2:
            return 0 # Break for new files
        
        sizeWeekly = CSVFile(self.WEEKLY_SIZE_FILE)
        sizeWeeklyRow = self.__daily2weeklyRow(currentlyUsed)
        previousNextWeek = sizeDaily.getRow(-2).get("next_week")
        self.__update_weekly_data(sizeWeekly, sizeWeeklyRow, previousNextWeek, nextWeek_,
                                  duplicateEmpty=1, updateLast=True)

        delta = subtract(sizeDaily.getRow(-1),sizeDaily.getRow(-2))
        diffDaily = CSVFile(self.DIFF_FILE)
        diffDaily.addRow(delta)
        diffDaily.efficientWriteFile()
        
        
        if sizeWeekly.length < 2:
            return 0 # Break for new files
        diffWeekly = CSVFile(self.WEEKLY_DIFF_FILE)
        diffWeeklyRow = subtract(sizeWeekly.getRow(-1), sizeWeekly.getRow(-2))
        print(delta)
        self.__update_weekly_data(diffWeekly, diffWeeklyRow, previousNextWeek, nextWeek_,
                                  makeEmpty=True)

if __name__ == '__main__':
    DiskUsage("/home/peter/scripts/datalogging/disk-usage/testfiles").update()