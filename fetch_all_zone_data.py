import sys
import os
sys.path.append(os.path.join(os.getcwd(),"static","bin","filter"))
from static.bin.fetch.gosatDataFetcher import *
from static.bin.fetch.oco2DataFetcher import *
from static.bin.filter.filterSWPR import *
from static.bin.filter.filterOCO2 import *

def collect(satellite,dateStart,dateEND,lat,long,radius):

    basePath=os.getcwd()
    date=dateStart
    if satellite=="OCO2":
        
        while (date<=dateEND):
            file=handle_oco2_fetch(date,basePath)
            if file != "":
                data=OCO2filter(file,None,date,1440,lat,long,radius)
                if len(data)<20:
                    os.remove(file)
            date=date+timedelta(days=1)
    elif satellite=="GOSAT":
        while (date<=dateEND):
            file=handle_gosat_fetch("SWPR",date,basePath)
            if file != "":
                data=SWPRfilter(file,"CO2","1590",date,1440,lat,long,radius)
                print(data)
                if len(data)<10:
                    os.remove(file)
            date=date+timedelta(days=1)

if __name__=="__main__":
    collect(""
        "GOSAT",
        datetime(year=2024,month=1,day=1),datetime(year=2024,month=12,day=31),
        48.8566,2.3522,
        300
    )