from datetime import timedelta

from static.bin.db.DeepBlueInserter import DeepBlueInserter
from static.bin.db.GOSATInserter import GOSATInserter
from static.bin.db.OCO2Inserter import OCO2Inserter
from static.bin.fetch.gosatDataFetcher import *
from static.bin.fetch.modisDataFetcher import handle_modis_fetch
from static.bin.fetch.oco2DataFetcher import *



import os
import re
from datetime import datetime



def find_file_by_date(path, file_type: str, date: datetime):



    if not os.path.isdir(path):

        raise ValueError(f"The path '{path}' is not a valid directory.")

    # Convert datetime to 'YYMMDD' string
    date_str ={ 'gosat': date.strftime('%Y%m%d'),
                'oco2': date.strftime('%y%m%d'),
                'modis_deep_blue': f"{date.year}{(date - datetime(day=1,month=1,year=date.year) + timedelta(days=1)).days:03d}"
    }

    # Define regex patterns for each file type
    patterns = {
        'gosat': re.compile(r'GOSAT2TFTS2(\d{8})_'),  # e.g. GOSAT2TFTS220220124_...
        'oco2': re.compile(r'oco2_LtCO2_(\d{6})_'),
        'modis_deep_blue': re.compile(r'AERDB_D3_VIIRS_NOAA20.A(\d{7})')
    }

    pattern = patterns.get(file_type.lower())
    if not pattern:
        raise ValueError("Unsupported file_type. Use 'gosat', 'oco2', or 'deepblue'.")



    for filename in os.listdir(path):
        match = pattern.search(filename)
        if match and match.group(1) == date_str[file_type.lower()]:
            return os.path.join(path, filename),True

    return "",False


def collect(satellite,lat,long,radius,start_date,end_date,basePath, localOnly, keepOption):


    date=start_date
    nbData=0

    if satellite=="OCO2":
        Dbcontroller= OCO2Inserter(os.path.join(basePath,"satelliteData.db"))
        while (date<=end_date):

            localDataPath= os.path.join(basePath,"data","OCO2",str(date.year))
            os.makedirs(localDataPath,exist_ok=True)
            file,foundLocally = find_file_by_date(localDataPath,"OCO2",date)

            if file == "" and not localOnly:
                file=handle_oco2_fetch(date,basePath)

            if file != "":
                data=Dbcontroller.process_file(lat,long,radius,file)
                nbData+=len(data)
                Dbcontroller.insert_data(data)

                if not keepOption and not localOnly and not foundLocally:
                    os.remove(file)

            date=date+timedelta(days=1)

    elif satellite=="GOSAT":

        Dbcontroller = GOSATInserter(os.path.join(basePath,"satelliteData.db"))
        Fetcher=  gosatDataFetcher(basePath)
        localDataPath= os.path.join(basePath,"data","GOSAT","SWPR")
        os.makedirs(localDataPath, exist_ok=True)


        while (date<=end_date):

            file,foundLocally= find_file_by_date(localDataPath,"GOSAT",date)

            if file == "" and not localOnly:
                file=Fetcher.handle_gosat_fetch("SWPR",date)

            if file != "":
                data=Dbcontroller.process_file(lat,long,radius,file)
                nbData += len(data)
                Dbcontroller.insert_data(data)

                if not keepOption and not localOnly and not foundLocally:
                    os.remove(file)

            date=date+timedelta(days=1)

    elif satellite=="MODIS_DEEP_BLUE":

        Dbcontroller = DeepBlueInserter(os.path.join(basePath,"satelliteData.db"))
        localDataPath= os.path.join(basePath,"data","MODIS","MODIS_DEEP_BLUE")
        os.makedirs(localDataPath,exist_ok=True)

        while (date<=end_date):

            file,foundLocally = find_file_by_date(localDataPath,"MODIS_DEEP_BLUE",date)


            if file == "" and not localOnly:
                file = handle_modis_fetch("MODIS_DEEP_BLUE",date,basePath)


            if file != "":
                data=Dbcontroller.process_file(lat,long,radius,date,file)
                nbData += len(data)
                Dbcontroller.insert_data(data)

                if not keepOption and not localOnly and not foundLocally:
                    os.remove(file)

            date = date + timedelta(days=1)


    return nbData