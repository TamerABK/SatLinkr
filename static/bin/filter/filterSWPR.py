from datetime import datetime,timedelta
from haversine import haversine,Unit
from .utils import *

import h5py

RETRIVALPATH={
    "CO2":{
        "2060":"RetrievalResult_B3_2060/XCO2_B3_2060",
        "1590":"RetrievalResult_B2_1590/XCO2_B2_1590"
    },
    "H2O":{
        "1590":"RetrievalResult_B2_1590/XH2O_B2_1590",
        "1660":"RetrievalResult_B2_1660/XH2O_B2_1660",
        "2060":"RetrievalResult_B3_2060/XH2O_B3_2060",
        "2350":"RetrievalResult_B3_2350/XH2O_B3_2350",
    },
    "CH4":{
        "1660":"RetrievalResult_B2_1660/XCH4_B2_1660",
        "2350":"RetrievalResult_B3_2350/XCH4_B3_2350"
    },
    "CO":{
        "2350":"RetrievalResult_B3_2350/XCO_B3_2350" 
    }
}

def SWPRfilter(file,gas,band,date:datetime,delta,lat,long,range):

    with h5py.File(file,'r') as fs:
        
        obs_time = convertToDatetime(fs["SoundingAttribute/observationTime"])
        index = np.arange(0,len(obs_time)) #List of non filtered indexes at first

        dateMin, dateMax= date -timedelta(minutes=delta),date +timedelta(minutes=delta)
        index=filterIndex(obs_time,index,dateMin,dateMax) 

        distances=[] #Calculate the distance between the center and the satellite observation using the haversine formula
        lats=fs["SoundingGeometry/latitude"]
        longs=fs["SoundingGeometry/longitude"]
        for lat2, long2 in zip(lats, longs):
            distances.append(distances.append(haversine((lat,long),(lat2,long2),unit=Unit.KILOMETERS)) ) 
        index=filterIndex(distances,index,None,range) 

        return [ [lats[i],longs[i],fs[RETRIVALPATH[gas][band]][i]] for i in index if fs[RETRIVALPATH[gas][band]][i]>=0.0]
    
if __name__=='__main__':
    print(
        SWPRfilter(
            "D:\Etudiant 5\Bureau\TAMER\satelliteImageryApp\data\GOSAT\SWPR\GOSAT2TFTS220240128_02SWPRV0210010017.h5",
            "CO2", "1590",
            datetime(day=28,month=1,year=2024,hour=12,minute=1), 60,
            0,0,900
        )
    )


