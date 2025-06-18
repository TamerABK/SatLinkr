import os
from datetime import datetime,timedelta
import sqlite3
from haversine import haversine, Unit


def haversine_sql(lat1, lon1, lat2, lon2):
    return haversine((lat1, lon1), (lat2, lon2), unit=Unit.KILOMETERS)

def get_column_names(basePath, table_name):
    conn = sqlite3.connect(os.path.join(basePath, 'satelliteData.db'))
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()
    return columns

def query_filter_for_csv(basePath, satellite, date: datetime, delta, lat, lon, radius):
    conn = sqlite3.connect(os.path.join(basePath, 'satelliteData.db'))
    conn.create_function("haversine", 4, haversine_sql)
    cursor = conn.cursor()

    if date is not None:
        with open(os.path.join(os.path.dirname(__file__), 'sql', "selectFilterForCSV.sql"), "r") as file:
            query = file.read()
            query = query.format(satellite=satellite)


        if satellite == "MODIS_DEEP_BLUE":
            date = date.replace(hour=23, minute=59, second=0, microsecond=0)
            delta=5

        time_start = (date - timedelta(minutes=delta)).timestamp()
        time_end = (date + timedelta(minutes=delta)).timestamp()
        params = (time_start, time_end, lat, lon, radius)

    else:
        with open(os.path.join(os.path.dirname(__file__), 'sql', "selectForAllDates.sql"), "r") as file:
            query = file.read()
            query = query.format(satellite=satellite)

        params = (lat, lon, radius)


    cursor.execute(query, params)
    results = cursor.fetchall()

    # Récupère les noms de colonnes
    header = get_column_names(basePath, satellite)

    conn.close()
    return header, results