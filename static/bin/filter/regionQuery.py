import os
import sqlite3
from datetime import datetime

from haversine import haversine, Unit


def haversine_sql(lat1, lon1, lat2, lon2):
    return haversine((lat1, lon1), (lat2, lon2), unit=Unit.KILOMETERS)

def get_all_regions(basePath):

    conn = sqlite3.connect(os.path.join(basePath, 'satelliteData.db'))
    cursor = conn.cursor()

    with open(os.path.join(os.path.dirname(__file__),'sql', "selectRegionsDetails.sql"), "r") as file:
        query = file.read()

    results = cursor.execute(query).fetchall()
    conn.close()
    return results

def get_region_dates(basePath,region):
    conn = sqlite3.connect(os.path.join(basePath, 'satelliteData.db'))
    cursor = conn.cursor()
    conn.create_function("haversine", 4, haversine_sql)

    with open(os.path.join(os.path.dirname(__file__), 'sql', "selectRegion.sql"), "r") as file:
        query = file.read()

    satellite, latitude, longitude, radius = cursor.execute(query, region).fetchone()

    with open(os.path.join(os.path.dirname(__file__), 'sql', "selectRegionAvailableDates.sql"), "r") as file:
        query = file.read()
        query = query.format(satellite=satellite)

    dates = cursor.execute(query,(latitude,longitude,radius)).fetchall()
    results = []
    for date in dates:
        results.append(datetime.fromtimestamp(date[0]).date())

    results = list(set(results))
    results.sort()
    conn.close()
    return results

def get_region(basePath,region):
    conn = sqlite3.connect(os.path.join(basePath, 'satelliteData.db'))
    cursor = conn.cursor()

    with open(os.path.join(os.path.dirname(__file__), 'sql', "selectRegion.sql"), "r") as file:
        query = file.read()

    results = cursor.execute(query,(region,)).fetchone()
    conn.close()
    return results
