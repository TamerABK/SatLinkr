import json
import os.path
import sqlite3
import numpy as np
from haversine import haversine, Unit
from netCDF4 import Dataset

from static.bin.db.BaseInserter import BaseInserter

def safe_extract(val, dtype=float, default=None):
    return dtype(val) if not np.ma.is_masked(val) else default

class OCO2Inserter(BaseInserter):
    def __init__(self, db_path):
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),'sql', 'insertOCO2.sql'), 'r') as f:
            self.insert_sql = f.read()
        super().__init__(db_path)

    def insert_data(self, data):
        try:
            self.cursor.executemany(self.insert_sql, data)
        except sqlite3.IntegrityError as e:
            print(f"[INSERT ERROR] IntegrityError: {e}")
            self.conn.rollback()
            raise
        except sqlite3.ProgrammingError as e:
            print(f"[INSERT ERROR] ProgrammingError: {e}")
            self.conn.rollback()
            raise
        except sqlite3.DatabaseError as e:
            print(f"[INSERT ERROR] DatabaseError: {e}")
            self.conn.rollback()
            raise
        except Exception as e:
            print(f"[INSERT ERROR] Unexpected error: {e}")
            self.conn.rollback()
            raise
        else:
            self.conn.commit()

    def process_file(self, lat, long, radius, filepath):
        data=[]
        with Dataset(filepath) as dt:

            dt.set_auto_mask(False)
            lats = np.float64(dt.variables['latitude'][:])
            longs = np.float64(dt.variables['longitude'][:])
            observationTimes = [int(t) for t in dt.variables['time'][:]]

            # Fetch other variables
            solar_zenith_angle = np.float64(dt.variables['solar_zenith_angle'][:])
            sensor_zenith_angle = np.float64(dt.variables['sensor_zenith_angle'][:])
            xco2_quality_flag = dt.variables['xco2_quality_flag'][:]
            xco2_qf_bitflag = dt.variables['xco2_qf_bitflag'][:]
            xco2_qf_simple_bitflag = dt.variables['xco2_qf_simple_bitflag'][:]
            xco2 = np.float64(dt.variables['xco2'][:])
            xco2_x2019 = np.float64(dt.variables['xco2_x2019'][:])
            xco2_uncertainty = np.float64(dt.variables['xco2_uncertainty'][:])
            xco2_apriori = np.float64(dt.variables['xco2_apriori'][:])
            pressure_levels = dt.variables['pressure_levels'][:]
            co2_profile_apriori = dt.variables['co2_profile_apriori'][:]
            xco2_averaging_kernel = dt.variables['xco2_averaging_kernel'][:]
            pressure_weight = dt.variables['pressure_weight'][:]

            for i in range(len(lats)):
                try:
                    if haversine((lat, long), (lats[i], longs[i]), unit=Unit.KILOMETERS) <= radius:

                        row = (
                            observationTimes[i],
                            lats[i],
                            longs[i],
                            solar_zenith_angle[i],
                            sensor_zenith_angle[i],
                            safe_extract(xco2_quality_flag[i],int,1),
                            safe_extract(xco2_qf_bitflag[i],int,1),
                            safe_extract(xco2_qf_simple_bitflag[i],int,1),
                            xco2[i],
                            xco2_x2019[i],
                            xco2_uncertainty[i],
                            xco2_apriori[i],
                            json.dumps(np.float32(pressure_levels[i]).tolist()),
                            json.dumps(np.float32(co2_profile_apriori[i]).tolist()),
                            json.dumps(np.float32(xco2_averaging_kernel[i]).tolist()),
                            json.dumps(np.float32(pressure_weight[i]).tolist())
                        )
                        data.append(row)
                except ValueError:
                    continue

        return data