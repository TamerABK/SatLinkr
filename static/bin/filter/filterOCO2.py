
from datetime import datetime,timedelta
from utils import *
from netCDF4 import Dataset
from haversine import haversine, Unit

def OCO2filter(file,gas,date:datetime,delta,lat,long,range,satellite_criteria):

    with Dataset(file, mode='r') as dt:
        
        obs_time = convertFromUnix(np.int64(dt.variables['time'][:]))
        index = np.arange(0,len(obs_time)) #List of non filtered indexes at first

        dateMin, dateMax= date -timedelta(minutes=delta),date +timedelta(minutes=delta)
        index=filterIndex(obs_time,index,dateMin,dateMax) 

        distances=[] #Calculate the distance between the center and the satellite observation using the haversine formula
        lats=np.float64(dt.variables['latitude'][:])
        longs=np.float64(dt.variables['longitude'][:])
        
        for lat2, long2 in zip(lats, longs):
            distances.append(haversine((lat,long),(lat2,long2),unit=Unit.KILOMETERS)) 
        index=filterIndex(distances,index,None,range) 
        
        if satellite_criteria == 'True':
            dt.set_auto_mask(False)
            var = dt.variables['xco2_qf_simple_bitflag']
            flags_raw = var[:]

            # Get missing value if available
            missing_value = getattr(var, 'missing_value', None)

            # Convert to int, handling missing values manually
            if missing_value is not None:
                mask = flags_raw == missing_value
                flags = flags_raw.astype(int)
                flags[mask] = 9999  # Or some other value/handling
            else:
                flags = flags_raw.astype(int)
    

            index= filterIndex(flags, index, None,1)


        return [ [lats[i],longs[i],np.float32(dt.variables["xco2"][i])] for i in index if np.float32(dt.variables["xco2"][i])>=0.0 and np.float32(dt.variables["xco2"][i]) < 999 ]
    
if __name__=='__main__':
    print(
        OCO2filter(
            "D:\Etudiant 5\Bureau\TAMER\satelliteImageryApp\data\OCO2\\2024\oco2_LtCO2_240101_B11210Ar_240919185807s.nc4",
            "CO2",
            datetime(day=1,month=1,year=2024,hour=12,minute=1), 360,
            0,0,900
        )
    )


