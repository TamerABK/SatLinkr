from datetime import datetime


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
