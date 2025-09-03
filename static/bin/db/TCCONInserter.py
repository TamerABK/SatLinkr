import os
import sqlite3

import numpy as np
from netCDF4 import Dataset, num2date

from static.bin.db.BaseInserter import BaseInserter

def safe_extract(val, default=None):
    return val if not np.ma.is_masked(val) else default

def ensure_datetime(d):
    if hasattr(d, 'datetime'):  # For cftime.Datetime
        return d.datetime
    return d  # Already datetime.datetime


def read_TCCON_netcdf(file):
    # Initialize an empty dictionary to hold the data
    data = {}

    # Open the NetCDF file
    with Dataset(file, 'r') as nc:
        # Read each variable and convert to float64 (equivalent to MATLAB's double)
        data['flag'] = np.float64(nc.variables['flag'][:])
        data['day'] = np.float64(nc.variables['day'][:])
        data['lat'] = np.float64(nc.variables['lat'][:])
        data['long'] = np.float64(nc.variables['long'][:])
        data['zobs'] = np.float64(nc.variables['zobs'][:])
        data['zmin'] = np.float64(nc.variables['zmin'][:])
        data['solzen'] = np.float64(nc.variables['solzen'][:])
        data['azim'] = np.float64(nc.variables['azim'][:])
        data['osds'] = np.float64(nc.variables['osds'][:])
        data['opd'] = np.float64(nc.variables['opd'][:])
        data['fovi'] = np.float64(nc.variables['fovi'][:])
        data['graw'] = np.float64(nc.variables['graw'][:])
        data['tins'] = np.float64(nc.variables['tins'][:])
        data['pins'] = np.float64(nc.variables['pins'][:])
        data['tout'] = np.float64(nc.variables['tout'][:])
        data['pout'] = np.float64(nc.variables['pout'][:])
        data['hout'] = np.float64(nc.variables['hout'][:])
        data['sia'] = np.float64(nc.variables['sia'][:])
        data['fvsi'] = np.float64(nc.variables['fvsi'][:])
        data['wspd'] = np.float64(nc.variables['wspd'][:])
        data['wdir'] = np.float64(nc.variables['wdir'][:])
        data['xluft'] = np.float64(nc.variables['xluft'][:])
        data['xhf'] = np.float64(nc.variables['xhf'][:])
        data['xh2o'] = np.float64(nc.variables['xh2o'][:])
        data['xhdo'] = np.float64(nc.variables['xhdo'][:])
        data['xco'] = np.float64(nc.variables['xco'][:])
        data['xn2o'] = np.float64(nc.variables['xn2o'][:])
        data['xch4'] = np.float64(nc.variables['xch4'][:])
        data['xco2'] = np.float64(nc.variables['xco2'][:])
        data['vsf_hcl'] = np.float64(nc.variables['vsf_hcl'][:])
        data['o2_7885_sg'] = np.float64(nc.variables['o2_7885_sg'][:])
        data['o2_7885_fs'] = np.float64(nc.variables['o2_7885_sg'][:])
        data['pmod'] = np.float64(nc.variables['pmod'][:])
        data['dip'] = np.float64(nc.variables['dip'][:])
        data['o2_7885_cl'] = np.float64(nc.variables['o2_7885_cl'][:])
        data['hour'] = np.float64(nc.variables['hour'][:])
        data['column_ch4'] = np.float64(nc.variables['column_ch4'][:])
        data['column_co2'] = np.float64(nc.variables['column_co2'][:])
        data['column_luft'] = np.float64(nc.variables['column_luft'][:])

        data['xco2_error'] = np.float64(nc.variables['xco2_error'][:])

        nomSPC = nc.variables['spectrum']

        nSPC = data['flag'].shape[0]

        timeData = nc.variables['time']
        time_units = timeData.units  # "seconds since 1970-01-01 00:00:00"
        time_calendar = getattr(timeData, 'calendar', 'standard')  # 'gregorian'

        # Convert to datetime objects
        data['date'] = [ensure_datetime(d).timestamp() for d in num2date(timeData[:], units=time_units, calendar=time_calendar,
                                                             only_use_cftime_datetimes=False)]

    return data


class TCCONInserter(BaseInserter):

    def __init__(self, db_path):
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),'sql', 'insertTCCON.sql'), 'r') as f:
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

    def add_station(self,station_name,lat,lon):

        try:
            self.cursor.execute("""
                                INSERT INTO fetched_regions (region_name, satellite, latitude, longitude, radius_km,
                                                             start_timestamp, end_timestamp, status, fetched_at,
                                                             created_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    station_name, 'TCCON', lat, lon, 2,
                                    0, 0, "Uploaded", 0, 0
                                ))
            self.conn.commit()
        except Exception as e:
            print(f"[INSERT ERROR] Unexpected error: {e}")
            self.conn.rollback()
            self.close()

    def process_file(self, file):
        data_dict = read_TCCON_netcdf(file)
        variable_names = [
            'flag', 'day', 'lat', 'long', 'zobs', 'zmin', 'solzen', 'azim', 'osds', 'opd', 'fovi', 'graw',
            'tins', 'pins', 'tout', 'pout', 'hout', 'sia', 'fvsi', 'wspd', 'wdir', 'xluft', 'xhf', 'xh2o',
            'xhdo', 'xco', 'xn2o', 'xch4', 'xco2', 'vsf_hcl', 'o2_7885_sg', 'o2_7885_fs', 'pmod', 'dip',
            'o2_7885_cl', 'hour', 'column_ch4', 'column_co2', 'column_luft', 'xco2_error', 'date'
        ]
        n = len(data_dict['flag'])
        rows = []
        for i in range(n):
            row = tuple(safe_extract(data_dict[var][i]) for var in variable_names)
            rows.append(row)
        return rows