import os
from datetime import datetime,timedelta
import sqlite3
from haversine import haversine, Unit


def haversine_sql(lat1, lon1, lat2, lon2):
    return haversine((lat1, lon1), (lat2, lon2), unit=Unit.KILOMETERS)

def query_oco2(basePath,date:datetime,delta,lat,lon,radius,quality_flag):

    conn = sqlite3.connect(os.path.join(basePath,'satelliteData.db'))

    # Register the haversine function into SQLite
    conn.create_function("haversine", 4, haversine_sql)

    cursor = conn.cursor()

    with open(os.path.join(os.path.dirname(__file__),'sql', "selectOCO2.sql"), "r") as file:
        query = file.read()

    time_start = (date - timedelta(minutes=delta)).timestamp()
    time_end = (date + timedelta(minutes=delta)).timestamp()

    if quality_flag == 'True':
        flag=1
    else:
        flag=2**31

    params = (time_start,time_end,lat,lon,radius)
    cursor.execute(query, params)
    results = cursor.fetchall()

    conn.close()
    return results
    
if __name__=='__main__':
    print(
       query_oco2(
           "C:\\Users\Enseignement\PycharmProjects\satelliteImageryApp",
           datetime.fromtimestamp(1704717161),
           720,
           48.8566, 2.3522, 300,
           True
       )
    )


