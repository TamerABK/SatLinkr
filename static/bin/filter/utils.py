import numpy as np
from datetime import datetime

# def haversine(lon1, lat1, lon2, lat2):
#     """
#     Calculate the great circle distance between two points
#     on the Earth (specified in decimal degrees).
#     """

#     lon1, lat1, lon2, lat2 = np.radians([lon1, lat1, lon2, lat2])

#     # Differences in coordinates
#     dlon = lon2 - lon1
#     dlat = lat2 - lat1

#     # Haversine formula
#     a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
#     c = 2 * np.arcsin(np.sqrt(a))
    
#     # Radius of the Earth in km
#     radius_of_earth = 6371.0

#     return c*2*radius_of_earth

def filterIndex(data,indexList,min,max):
    filteredIndex=[]
    for i in indexList:
        if (min==None or min<= data[i]) and (max==None or data[i] <= max):
            filteredIndex.append(i)
    return filteredIndex

def convertToDatetime(observationTime):
    decoded_times = [t.decode('utf-8') for t in observationTime]
    timestamps = [datetime.fromisoformat(t.rstrip('Z')) for t in decoded_times]
    return timestamps

def convertFromUnix(observationTime):
    return [datetime.fromtimestamp(t).replace(second=0) for t in observationTime]
