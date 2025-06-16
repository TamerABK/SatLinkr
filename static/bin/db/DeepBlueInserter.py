import json
import os
import sqlite3
from datetime import datetime

import numpy as np
from haversine import Unit, haversine
from netCDF4 import Dataset

from static.bin.db.BaseInserter import BaseInserter

def safe_extract(value, cast_type, default=None):
    try:
        return cast_type(value)
    except Exception:
        return default


class DeepBlueInserter(BaseInserter):

    def __init__(self,db_path):
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),'sql', 'insertDEEPBLUE.sql'), 'r') as f:
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

    def process_file(self,lat, long, radius,date:datetime, filepath):
        data = []

        with Dataset(filepath) as dt:
            dt.set_auto_mask(False)

            # Read and flatten latitude/longitude
            lats = np.float64( dt.variables['Latitude'][:].flatten())
            longs = np.float64( dt.variables['Longitude'][:].flatten())

            # Flatten 2D variables
            vars_2d = [
                "Aerosol_Optical_Thickness_550_Land_Count",
                "Aerosol_Optical_Thickness_550_Land_Maximum",
                "Aerosol_Optical_Thickness_550_Land_Mean",
                "Aerosol_Optical_Thickness_550_Land_Minimum",
                "Aerosol_Optical_Thickness_550_Land_Standard_Deviation",
                "Angstrom_Exponent_Land_Maximum",
                "Angstrom_Exponent_Land_Mean",
                "Angstrom_Exponent_Land_Minimum",
                "Angstrom_Exponent_Land_Standard_Deviation"
            ]
            flattened_2d = {var: dt.variables[var][:].flatten() for var in vars_2d}

            # Flatten 3D variables: each will be a list of 1D arrays (one for each channel)
            vars_3d = [
                "Spectral_Aerosol_Optical_Thickness_Land_Count",
                "Spectral_Aerosol_Optical_Thickness_Land_Mean",
                "Spectral_Aerosol_Optical_Thickness_Land_Standard_Deviation"
            ]
            flattened_3d = {
                var: [dt.variables[var][i, :, :].flatten() for i in range(dt.variables[var].shape[0])]
                for var in vars_3d
            }


            num_points = lats.shape[0]
            for i in range(num_points):
                try:
                    if haversine((lat, long), (lats[i], longs[i]), unit=Unit.KILOMETERS) <= radius and flattened_2d["Aerosol_Optical_Thickness_550_Land_Count"][i] > 0 :
                        row = (
                            date.timestamp(),
                            lats[i],
                            longs[i],
                            *[safe_extract(flattened_2d[var][i], float, np.nan) for var in vars_2d],
                            *[
                                safe_extract(channel[i], float, np.nan)
                                for var in vars_3d
                                for channel in flattened_3d[var]
                            ]
                        )
                        data.append(row)
                except Exception:
                    continue

        return data


if __name__ == "__main__":

    db = DeepBlueInserter('temp.db')

    print(db.process_file(48.8566,2.5422,300,datetime(year=2024,month=4,day=12),"C:\\Users\Enseignement\PycharmProjects\satelliteImageryApp\data\MODIS\Deep Blue\AERDB_D3_VIIRS_NOAA20.A2024102.002.2024106000512.nc"))