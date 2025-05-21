import json
import os
import sqlite3

import h5py
import numpy as np
from haversine import haversine, Unit

from static.bin.db.BaseInserter import BaseInserter


class GOSATInserter(BaseInserter):

    def __init__(self, db_path):
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),'sql', 'insertGOSAT.sql'), 'r') as f:
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

    def process_file(self,lat,long,radius,filepath):

        data = []

        with h5py.File(filepath, 'r') as fs:

            observationTimes= [self.convert_iso_to_unix(iso_str) for iso_str in fs["SoundingAttribute/observationTime"][:]]
            lats = np.float64(fs["SoundingGeometry/latitude"][:])
            longs = np.float64(fs["SoundingGeometry/longitude"][:])
            solarZenith = np.float64(fs["SoundingGeometry/solarZenith"][:])
            XCH4_B3_2350 = np.float64(fs["RetrievalResult_B3_2350/XCH4_B3_2350"][:])
            XCH4_apriori_B3_2350 = np.float64(fs["RetrievalResult_B3_2350/XCH4_apriori_B3_2350"][:])
            XCH4_dfs_B3_2350 = np.float64(fs["RetrievalResult_B3_2350/XCH4_dfs_B3_2350"][:])
            XCH4_uncert_B3_2350 = np.float64(fs["RetrievalResult_B3_2350/XCH4_uncert_B3_2350"][:])
            XCO_B3_2350 = np.float64(fs["RetrievalResult_B3_2350/XCO_B3_2350"][:])
            XCO_apriori_B3_2350 = np.float64(fs["RetrievalResult_B3_2350/XCO_apriori_B3_2350"][:])
            XCO_dfs_B3_2350 = np.float64(fs["RetrievalResult_B3_2350/XCO_dfs_B3_2350"][:])
            XCO_uncert_B3_2350 = np.float64(fs["RetrievalResult_B3_2350/XCO_uncert_B3_2350"][:])
            XH2O_B3_2350 = np.float64(fs["RetrievalResult_B3_2350/XH2O_B3_2350"][:])
            XH2O_apriori_B3_2350 = np.float64(fs["RetrievalResult_B3_2350/XH2O_apriori_B3_2350"][:])
            XH2O_dfs_B3_2350 = np.float64(fs["RetrievalResult_B3_2350/XH2O_dfs_B3_2350"][:])
            XH2O_uncert_B3_2350 = np.float64(fs["RetrievalResult_B3_2350/XH2O_uncert_B3_2350"][:])
            XCO2_B2_1590 = np.float64(fs["RetrievalResult_B2_1590/XCO2_B2_1590"][:])
            XCO2_apriori_B2_1590 = np.float64(fs["RetrievalResult_B2_1590/XCO2_apriori_B2_1590"][:])
            XCO2_dfs_B2_1590 = np.float64(fs["RetrievalResult_B2_1590/XCO2_dfs_B2_1590"][:])
            XCO2_uncert_B2_1590 = np.float64(fs["RetrievalResult_B2_1590/XCO2_uncert_B2_1590"][:])
            XCO2_B3_2060 = np.float64(fs["RetrievalResult_B3_2060/XCO2_B3_2060"][:])
            XCO2_apriori_B3_2060 = np.float64(fs["RetrievalResult_B3_2060/XCO2_apriori_B3_2060"][:])
            XCO2_dfs_B3_2060 = np.float64(fs["RetrievalResult_B3_2060/XCO2_dfs_B3_2060"][:])
            XCO2_uncert_B3_2060 = np.float64(fs["RetrievalResult_B3_2060/XCO2_uncert_B3_2060"][:])
            XCH4_B2_1660 = np.float64(fs["RetrievalResult_B2_1660/XCH4_B2_1660"][:])
            XCH4_apriori_B2_1660 = np.float64(fs["RetrievalResult_B2_1660/XCH4_apriori_B2_1660"][:])
            XCH4_dfs_B2_1660 = np.float64(fs["RetrievalResult_B2_1660/XCH4_dfs_B2_1660"][:])
            XCH4_uncert_B2_1660 = np.float64(fs["RetrievalResult_B2_1660/XCH4_uncert_B2_1660"][:])
            XH2O_B3_2060 = np.float64(fs["RetrievalResult_B3_2060/XH2O_B3_2060"][:])
            XH2O_apriori_B3_2060 = np.float64(fs["RetrievalResult_B3_2060/XH2O_apriori_B3_2060"][:])
            XH2O_dfs_B3_2060 = np.float64(fs["RetrievalResult_B3_2060/XH2O_dfs_B3_2060"][:])
            XH2O_uncert_B3_2060 = np.float64(fs["RetrievalResult_B3_2060/XH2O_uncert_B3_2060"][:])
            XH2O_B2_1660 = np.float64(fs["RetrievalResult_B2_1660/XH2O_B2_1660"][:])
            XH2O_apriori_B2_1660 = np.float64(fs["RetrievalResult_B2_1660/XH2O_apriori_B2_1660"][:])
            XH2O_dfs_B2_1660 = np.float64(fs["RetrievalResult_B2_1660/XH2O_dfs_B2_1660"][:])
            XH2O_uncert_B2_1660 = np.float64(fs["RetrievalResult_B2_1660/XH2O_uncert_B2_1660"][:])
            XH2O_B2_1590 = np.float64(fs["RetrievalResult_B2_1590/XH2O_B2_1590"][:])
            XH2O_apriori_B2_1590 = np.float64(fs["RetrievalResult_B2_1590/XH2O_apriori_B2_1590"][:])
            XH2O_dfs_B2_1590 = np.float64(fs["RetrievalResult_B2_1590/XH2O_dfs_B2_1590"][:])
            XH2O_uncert_B2_1590 = np.float64(fs["RetrievalResult_B2_1590/XH2O_uncert_B2_1590"][:])
            algorithmName = fs["Metadata/algorithmName"][0]
            algorithmVersion = fs["Metadata/algorithmVersion"][0]
            soundingQualityFlag = fs["L1QualityInfo/soundingQualityFlag"][:]
            spectrumQualityFlag = fs["L1QualityInfo/spectrumQualityFlag"][:]

            for i in range(lats.size):
                try:

                    if haversine((lat, long), (lats[i], longs[i]), unit=Unit.KILOMETERS) <= radius:
                        row = (
                            observationTimes[i],  # observationTime
                            lats[i],  # latitude
                            longs[i],  # longitude
                            solarZenith[i],  # solar_zenith_angle
                            XCH4_B3_2350[i],  # XCH4_B3_2350
                            XCH4_apriori_B3_2350[i],  # XCH4_apriori_B3_2350
                            XCH4_dfs_B3_2350[i],  # XCH4_dfs_B3_2350
                            XCH4_uncert_B3_2350[i],  # XCH4_uncert_B3_2350
                            XCO_B3_2350[i],  # XCO_B3_2350
                            XCO_apriori_B3_2350[i],  # XCO_apriori_B3_2350
                            XCO_dfs_B3_2350[i],  # XCO_dfs_B3_2350
                            XCO_uncert_B3_2350[i],  # XCO_uncert_B3_2350
                            XH2O_B3_2350[i],  # XH2O_B3_2350
                            XH2O_apriori_B3_2350[i],  # XH2O_apriori_B3_2350
                            XH2O_dfs_B3_2350[i],  # XH2O_dfs_B3_2350
                            XH2O_uncert_B3_2350[i],  # XH2O_uncert_B3_2350
                            XCO2_B2_1590[i],  # XCO2_B2_1590
                            XCO2_apriori_B2_1590[i],  # XCO2_apriori_B2_1590
                            XCO2_dfs_B2_1590[i],  # XCO2_dfs_B2_1590
                            XCO2_uncert_B2_1590[i],  # XCO2_uncert_B2_1590
                            XCO2_B3_2060[i],  # XCO2_B3_2060
                            XCO2_apriori_B3_2060[i],  # XCO2_apriori_B3_2060
                            XCO2_dfs_B3_2060[i],  # XCO2_dfs_B3_2060
                            XCO2_uncert_B3_2060[i],  # XCO2_uncert_B3_2060
                            XCH4_B2_1660[i],  # XCH4_B2_1660
                            XCH4_apriori_B2_1660[i],  # XCH4_apriori_B2_1660
                            XCH4_dfs_B2_1660[i],  # XCH4_dfs_B2_1660
                            XCH4_uncert_B2_1660[i],  # XCH4_uncert_B2_1660
                            XH2O_B3_2060[i],  # XH2O_B3_2060
                            XH2O_apriori_B3_2060[i],  # XH2O_apriori_B3_2060
                            XH2O_dfs_B3_2060[i],  # XH2O_dfs_B3_2060
                            XH2O_uncert_B3_2060[i],  # XH2O_uncert_B3_2060
                            XH2O_B2_1660[i],  # XH2O_B2_1660
                            XH2O_apriori_B2_1660[i],  # XH2O_apriori_B2_1660
                            XH2O_dfs_B2_1660[i],  # XH2O_dfs_B2_1660
                            XH2O_uncert_B2_1660[i],  # XH2O_uncert_B2_1660
                            XH2O_B2_1590[i],  # XH2O_B2_1590
                            XH2O_apriori_B2_1590[i],  # XH2O_apriori_B2_1590
                            XH2O_dfs_B2_1590[i],  # XH2O_dfs_B2_1590
                            XH2O_uncert_B2_1590[i],  # XH2O_uncert_B2_1590
                            str(algorithmName.decode('utf-8')),  # algorithmName
                            str(algorithmVersion.decode('utf-8')),  # algorithmVersion
                            str(soundingQualityFlag[i].decode('utf-8')),  # soundingQualityFlag
                            json.dumps(spectrumQualityFlag[i].tolist())  # spectrumQualityFlag
                        )

                        data.append(row)

                except ValueError:
                    continue

        return data