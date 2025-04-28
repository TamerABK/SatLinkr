import os
import sqlite3
from datetime import datetime,timedelta
from haversine import haversine,Unit
from utils import *

import h5py

OPTIONS={
    "CO2":{
        "2060":"XCO2_B3_2060",
        "1590":"XCO2_B2_1590"
    },
    "H2O":{
        "1590":"XH2O_B2_1590",
        "1660":"XH2O_B2_1660",
        "2060":"XH2O_B3_2060",
        "2350":"XH2O_B3_2350",
    },
    "CH4":{
        "1660":"XCH4_B2_1660",
        "2350":"XCH4_B3_2350"
    },
    "CO":{
        "2350":"XCO_B3_2350"
    }
}

def haversine_sql(lat1, lon1, lat2, lon2):
    return haversine((lat1, lon1), (lat2, lon2), unit=Unit.KILOMETERS)

def query_gosat(basePath,gas,band,date:datetime,delta,lat,lon,radius):

    conn = sqlite3.connect(os.path.join(basePath, 'satelliteData.db'))

    # Register the haversine function into SQLite
    conn.create_function("haversine", 4, haversine_sql)

    cursor = conn.cursor()

    with open(os.path.join(os.path.dirname(__file__), 'sql', "selectGOSAT.sql"), "r") as file:
        query = file.read()
        query = query.format(field_name=OPTIONS[gas][band])

    time_start = (date - timedelta(minutes=delta)).timestamp()
    time_end = (date + timedelta(minutes=delta)).timestamp()


    params = (time_start, time_end, lat, lon, radius)
    cursor.execute(query, params)
    results = cursor.fetchall()

    conn.close()
    return results
    
if __name__=='__main__':
    print(
        query_gosat(
            "C:\\Users\Enseignement\PycharmProjects\satelliteImageryApp",
            'CO2','2060',
            datetime.fromtimestamp(1704197928),
            720,
            48.8566, 2.3522, 300,
        )
    )


