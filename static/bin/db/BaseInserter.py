import os.path
import sqlite3
from datetime import datetime

from haversine import haversine, Unit


def haversine_sql(lat1, lon1, lat2, lon2):
    # Using the haversine library's function
    return haversine((lat1, lon1), (lat2, lon2), unit=Unit.KILOMETERS)

def convertToDatetime(observationTime):
    decoded_times = [t.decode('utf-8') for t in observationTime]
    timestamps = [datetime.fromisoformat(t.rstrip('Z')) for t in decoded_times]
    return timestamps

class BaseInserter:

    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.create_function("haversine", 4, haversine_sql)
        self.cursor = self.conn.cursor()
        self.create_table_if_not_exists()

    def convert_iso_to_unix(self, iso_str):
        return int(datetime.fromisoformat(iso_str.decode('utf-8').rstrip('Z')).timestamp())

    def create_table_if_not_exists(self):
        with open(os.path.join(os.path.dirname(__file__),'sql','tables.sql'), "r") as file:
            self.cursor.executescript(file.read())
            self.conn.commit()

    def insert_data(self, data):
        raise NotImplementedError("Subclasses must implement this.")

    def close(self):
        self.conn.commit()
        self.conn.close()