import os
from datetime import datetime,timedelta
import sqlite3
from haversine import haversine, Unit


def haversine_sql(lat1, lon1, lat2, lon2):
    return haversine((lat1, lon1), (lat2, lon2), unit=Unit.KILOMETERS)


def query_deepblue(basePath,field,band,date:datetime,delta,lat,lon,radius):
    conn = sqlite3.connect(os.path.join(basePath, 'satelliteData.db'))

    # Register the haversine function into SQLite
    conn.create_function("haversine", 4, haversine_sql)

    cursor = conn.cursor()

    if band != 'None':
        field = f"{field}_{band}"

    with open(os.path.join(os.path.dirname(__file__), 'sql', "selectDeepBlue.sql"), "r") as file:
        query = file.read()
        query = query.format(field_name=field)

    time_start = (date - timedelta(minutes=delta)).timestamp()
    time_end = (date + timedelta(minutes=delta)).timestamp()

    params = (time_start, time_end, lat, lon, radius)
    cursor.execute(query, params)
    results = cursor.fetchall()

    conn.close()
    print(params)
    print(results)
    return results