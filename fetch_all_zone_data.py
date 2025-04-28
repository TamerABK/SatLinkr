import sys
import os

from static.bin.db.GOSATInserter import GOSATInserter
from static.bin.db.OCO2Inserter import OCO2Inserter

sys.path.append(os.path.join(os.getcwd(),"static","bin","filter"))
from static.bin.fetch.gosatDataFetcher import *
from static.bin.fetch.oco2DataFetcher import *
from static.bin.filter.filterSWPR import *
from static.bin.filter.filterOCO2 import *

def collect(satellite,year,lat,long,radius): 

    dateStart,dateEND=  datetime(year=year,month=6,day=17),datetime(year=year,month=12,day=31)

    basePath=os.getcwd()
    date=dateStart


    if satellite=="OCO2":
        Dbcontroller= OCO2Inserter(os.path.join(basePath,"satelliteData.db"))
        while (date<=dateEND):
            file=handle_oco2_fetch(date,basePath)
            if file != "":
                data=Dbcontroller.process_file(lat,long,radius,file)
                Dbcontroller.insert_data(data)

            date=date+timedelta(days=1)
    elif satellite=="GOSAT":
        Dbcontroller= GOSATInserter(os.path.join(basePath,"satelliteData.db"))
        Fetcher=  gosatDataFetcher(basePath)
        while (date<=dateEND):
            file=Fetcher.handle_gosat_fetch("SWPR",date)
            if file != "":
                data=Dbcontroller.process_file(lat,long,radius,file)
                Dbcontroller.insert_data(data)
            print(date,file)
            date=date+timedelta(days=1)

if __name__=="__main__":
    collect(
        "GOSAT",
        2023,
        48.8566,2.3522,
        300 
    )