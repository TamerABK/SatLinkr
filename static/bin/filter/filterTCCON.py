import os
import sqlite3
from datetime import datetime, timedelta

from haversine import haversine, Unit

from static.bin.filter.filterSWPR import OPTIONS

OPTIONS= {
    "CO2": "xco2",
    "CH4": "xch4",
    "CO": "xco",
    "H2O": "xh2o"}

def haversine_sql(lat1, lon1, lat2, lon2):
    return haversine((lat1, lon1), (lat2, lon2), unit=Unit.KILOMETERS)

def query_tccon(basePath,gas,date:datetime,delta,lat,lon,radius):

    if gas not in OPTIONS:
        return []

    conn = sqlite3.connect(os.path.join(basePath, 'satelliteData.db'))


    # Register the haversine function into SQLite
    conn.create_function("haversine", 4, haversine_sql)

    cursor = conn.cursor()

    with open(os.path.join(os.path.dirname(__file__), 'sql', "selectTCCON.sql"), "r") as file:
        query = file.read()
        query = query.format(field_name=OPTIONS[gas])

    time_start = (date - timedelta(minutes=delta)).timestamp()
    time_end = (date + timedelta(minutes=delta)).timestamp()


    params = (time_start, time_end, lat, lon, radius)
    cursor.execute(query, params)
    results = cursor.fetchall()

    conn.close()


    return results