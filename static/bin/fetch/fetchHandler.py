import os
import sqlite3
import time
from datetime import datetime

from static.bin.fetch.fetch_all_zone_data import collect

class FetchHandler:
    def __init__(self, basePath):
        self.basePath = basePath
        self.conn = sqlite3.connect(os.path.join(basePath,'satelliteData.db'))
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def _region_exists(self, lat, lon, radius_km):
        self.cursor.execute("""
            SELECT region_name FROM fetched_regions
            WHERE latitude = ? AND longitude = ? AND radius_km = ?
        """, (lat, lon, radius_km))
        return self.cursor.fetchone()

    def _name_conflict(self, region_name, lat, lon, radius_km):
        self.cursor.execute("""
            SELECT latitude, longitude, radius_km FROM fetched_regions
            WHERE region_name = ?
        """, (region_name,))
        row = self.cursor.fetchone()
        if not row:
            return False
        return (
            float(row["latitude"]) != lat or
            float(row["longitude"]) != lon or
            float(row["radius_km"]) != radius_km
        )

    def _fetch_overlap(self, region_name, start_ts, end_ts):
        self.cursor.execute("""
            SELECT * FROM fetched_regions
            WHERE region_name = ?
              AND (
                  (? >= start_timestamp AND ? <= end_timestamp) OR
                  (? <= end_timestamp AND ? >= start_timestamp)
              )
        """, (region_name, start_ts, end_ts, start_ts, end_ts))
        return self.cursor.fetchone()

    def _get_existing_range(self, region_name):
        self.cursor.execute("""
            SELECT start_timestamp, end_timestamp FROM fetched_regions
            WHERE region_name = ?
        """, (region_name,))
        return self.cursor.fetchone()

    def register_fetch(self, region_name, satellite, lat, lon, radius_km, start_date:datetime, end_date:datetime, localOnly, keepOption):

        start_ts, end_ts = start_date.timestamp(), end_date.timestamp()

        # 1. Prevent same lat/lon/radius with different name
        try:
            print("About to call _region_exists()")
            existing = self._region_exists(lat, lon, radius_km)
            print("Existing region:", existing)
        except Exception as e:
            print("Error calling _region_exists():", e)
            raise
        if existing and existing["region_name"] != region_name:
            raise ValueError(f"Region with same coordinates already exists as '{existing['region_name']}'.")

        # 2. Prevent same name with different coordinates
        if self._name_conflict(region_name, lat, lon, radius_km):
            raise ValueError(f"Region name '{region_name}' already used for different coordinates.")

        # 3. Check for full coverage
        overlap = self._fetch_overlap(region_name, start_ts, end_ts)
        if overlap and start_ts >= overlap["start_timestamp"] and end_ts <= overlap["end_timestamp"]:
            raise ValueError(f"This period is already fetched for region '{region_name}'.")

        now_ts = int(time.time())

        print(f"About to fetch region '{region_name}'")
        nbData = collect(satellite, lat, lon, radius_km, start_date, end_date, self.basePath,localOnly, keepOption)

        if nbData == 0:
            fetchStatus = "No data available"
        else:
            fetchStatus = "Data fetched"

        # 5. Create new region entry
        self.cursor.execute("""
            INSERT INTO fetched_regions (
                region_name, satellite, latitude, longitude, radius_km,
                start_timestamp, end_timestamp, status, fetched_at, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            region_name, satellite, lat, lon, radius_km,
            start_ts, end_ts,fetchStatus, now_ts, now_ts
        ))
        self.conn.commit()
        return "New region fetch registered."

    def close(self):
        self.conn.close()
