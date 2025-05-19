from datetime import timedelta
from static.bin.db.GOSATInserter import GOSATInserter
from static.bin.db.OCO2Inserter import OCO2Inserter
from static.bin.fetch.gosatDataFetcher import *
from static.bin.fetch.oco2DataFetcher import *



import os
import re
from datetime import datetime
from typing import Optional

def find_file_by_date(path, file_type: str, date: datetime) -> Optional[str]:


    if not os.path.isdir(path):
        raise ValueError(f"The path '{path}' is not a valid directory.")

    # Convert datetime to 'YYMMDD' string
    date_str ={ 'gosat': date.strftime('%Y%m%d'),
                'oco2': date.strftime('%y%m%d')
    }

    # Define regex patterns for each file type
    patterns = {
        'gosat': re.compile(r'GOSAT.*?(\d{6})_'),        # e.g. GOSAT2TFTS220324_...
        'oco2': re.compile(r'oco2_LtCO2_(\d{6})_'),      # e.g. oco2_LtCO2_220324_...
    }

    pattern = patterns.get(file_type.lower())
    if not pattern:
        raise ValueError("Unsupported file_type. Use 'gosat' or 'oco2'.")


    for filename in os.listdir(path):
        match = pattern.search(filename)
        if match and match.group(1) == date_str[file_type.lower()]:
            return os.path.join(path, filename)

    return ""


def collect(satellite,lat,long,radius,start_date,end_date,basePath, localOnly, keepOption):


    date=start_date
    nbData=0

    if satellite=="OCO2":
        Dbcontroller= OCO2Inserter(os.path.join(basePath,"satelliteData.db"))
        while (date<=end_date):

            localDataPath= os.path.join(basePath,"data","OCO2",str(date.year))
            os.makedirs(localDataPath,exist_ok=True)
            file = find_file_by_date(localDataPath,"OCO2",date)

            if file == "" and not localOnly:
                file=handle_oco2_fetch(date,basePath)

            if file != "":
                data=Dbcontroller.process_file(lat,long,radius,file)
                nbData+=len(data)
                Dbcontroller.insert_data(data)

                if not keepOption and not localOnly:
                    os.remove(file)

            date=date+timedelta(days=1)

    elif satellite=="GOSAT":

        Dbcontroller= GOSATInserter(os.path.join(basePath,"satelliteData.db"))
        Fetcher=  gosatDataFetcher(basePath)
        localDataPath= os.path.join(basePath,"data","GOSAT","SWPR")

        while (date<=end_date):

            file= find_file_by_date(localDataPath,"GOSAT",date)

            if file == "" and not localOnly:
                file=Fetcher.handle_gosat_fetch("SWPR",date)

            if file != "":
                data=Dbcontroller.process_file(lat,long,radius,file)
                nbData += len(data)
                Dbcontroller.insert_data(data)

                if not keepOption and not localOnly:
                    os.remove(file)

            date=date+timedelta(days=1)



    return nbData