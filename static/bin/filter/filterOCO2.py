
from datetime import datetime,timedelta
from utils import *
from netCDF4 import Dataset
from haversine import haversine, Unit

def OCO2filter(file,gas,date:datetime,delta,lat,long,range):

    with Dataset(file, mode='r') as fs:
        
        obs_time = convertFromUnix(np.int64(fs.variables['time'][:]))
        index = np.arange(0,len(obs_time)) #List of non filtered indexes at first

        dateMin, dateMax= date -timedelta(minutes=delta),date +timedelta(minutes=delta)
        index=filterIndex(obs_time,index,dateMin,dateMax) 

        distances=[] #Calculate the distance between the center and the satellite observation using the haversine formula
        lats=np.float64(fs.variables['latitude'][:])
        longs=np.float64(fs.variables['longitude'][:])
        for lat2, long2 in zip(lats, longs):
            distances.append(haversine((lat,long),(lat2,long2),unit=Unit.KILOMETERS)) 
        index=filterIndex(distances,index,None,range) 
        print([distances[i] for i in index])
        return [ [lats[i],longs[i],np.float32(fs.variables["xco2"][i])] for i in index if np.float32(fs.variables["xco2"][i])>=0.0 and np.float32(fs.variables["xco2"][i]) < 999 ]
    
if __name__=='__main__':
    print(
        OCO2filter(
            "D:\Etudiant 5\Bureau\TAMER\satelliteImageryApp\data\OCO2\\2024\oco2_LtCO2_240101_B11210Ar_240919185807s.nc4",
            "CO2",
            datetime(day=1,month=1,year=2024,hour=12,minute=1), 360,
            0,0,900
        )
    )


