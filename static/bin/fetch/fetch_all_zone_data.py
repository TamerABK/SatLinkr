from datetime import timedelta

from flask_socketio import SocketIO, emit

from static.bin.db.DeepBlueInserter import DeepBlueInserter
from static.bin.db.GOSATInserter import GOSATInserter
from static.bin.db.OCO2Inserter import OCO2Inserter
from static.bin.fetch.gosatDataFetcher import *
from static.bin.fetch.modisDataFetcher import handle_modis_fetch
from static.bin.fetch.oco2DataFetcher import *



import os
import re
from datetime import datetime



def find_file_by_date(path, file_type: str, date: datetime):



    if not os.path.isdir(path):

        raise ValueError(f"The path '{path}' is not a valid directory.")

    # Convert datetime to 'YYMMDD' string
    date_str ={ 'gosat': date.strftime('%Y%m%d'),
                'oco2': date.strftime('%y%m%d'),
                'modis_deep_blue': f"{date.year}{(date - datetime(day=1,month=1,year=date.year) + timedelta(days=1)).days:03d}"
    }

    # Define regex patterns for each file type
    patterns = {
        'gosat': re.compile(r'GOSAT2TFTS2(\d{8})_'),  # e.g. GOSAT2TFTS220220124_...
        'oco2': re.compile(r'oco2_LtCO2_(\d{6})_'),
        'modis_deep_blue': re.compile(r'AERDB_D3_VIIRS_NOAA20.A(\d{7})')
    }

    pattern = patterns.get(file_type.lower())
    if not pattern:
        raise ValueError("Unsupported file_type. Use 'gosat', 'oco2', or 'deepblue'.")



    for filename in os.listdir(path):
        match = pattern.search(filename)
        if match and match.group(1) == date_str[file_type.lower()]:
            return os.path.join(path, filename),True

    return "",False


def collect(satellite, lat, long, radius, start_date, end_date, basePath, localOnly, keepOption, socketio: SocketIO):
    date = start_date
    nbData = 0

    if satellite == "OCO2":
        try:
            Dbcontroller = OCO2Inserter(os.path.join(basePath, "satelliteData.db"))
        except Exception as e:
            print(f"Erreur lors de l'initialisation du contrôleur OCO2 : {e}")
            return nbData

        while date <= end_date:

            try:
                socketio.emit('fetch_progress',
                          {'current': (date - start_date).days + 1, 'total': (end_date - start_date).days + 1})
            except Exception as e:
                print(f"Erreur lors de l'émission du progrès via SocketIO : {e}")

            try:
                localDataPath = os.path.join(basePath, "data", "OCO2", str(date.year))
                os.makedirs(localDataPath, exist_ok=True)
                file, foundLocally = find_file_by_date(localDataPath, "OCO2", date)

                if file == "" and not localOnly:
                    try:
                        file = handle_oco2_fetch(date, basePath)
                    except Exception as e:
                        print(f"Erreur lors du téléchargement OCO2 pour {date} : {e}")
                        file = ""

                if file != "":
                    try:
                        data = Dbcontroller.process_file(lat, long, radius, file)
                        nbData += len(data)
                        Dbcontroller.insert_data(data)
                    except Exception as e:
                        print(f"Erreur lors du traitement/insertion OCO2 pour {file} : {e}")

                    if not keepOption and not localOnly and not foundLocally:
                        try:
                            os.remove(file)
                        except Exception as e:
                            print(f"Erreur lors de la suppression du fichier {file} : {e}")

            except Exception as e:
                print(f"Erreur générale OCO2 pour la date {date} : {e}")


            date = date + timedelta(days=1)


    elif satellite == "GOSAT":
        try:
            Dbcontroller = GOSATInserter(os.path.join(basePath, "satelliteData.db"))
            Fetcher = gosatDataFetcher(basePath)
            localDataPath = os.path.join(basePath, "data", "GOSAT", "SWPR")
            os.makedirs(localDataPath, exist_ok=True)
        except Exception as e:
            print(f"Erreur lors de l'initialisation du contrôleur/fetcher GOSAT : {e}")
            return nbData

        while date <= end_date:

            try:
                socketio.emit('fetch_progress',
                          {'current': (date - start_date).days + 1, 'total': (end_date - start_date).days + 1})
            except Exception as e:
                print(f"Erreur lors de l'émission du progrès via SocketIO : {e}")

            try:
                file, foundLocally = find_file_by_date(localDataPath, "GOSAT", date)

                if file == "" and not localOnly:
                    try:
                        file = Fetcher.handle_gosat_fetch("SWPR", date)
                    except Exception as e:
                        print(f"Erreur lors du téléchargement GOSAT pour {date} : {e}")
                        file = ""

                if file != "":
                    try:
                        data = Dbcontroller.process_file(lat, long, radius, file)
                        nbData += len(data)
                        Dbcontroller.insert_data(data)
                    except Exception as e:
                        print(f"Erreur lors du traitement/insertion GOSAT pour {file} : {e}")

                    if not keepOption and not localOnly and not foundLocally:
                        try:
                            os.remove(file)
                        except Exception as e:
                            print(f"Erreur lors de la suppression du fichier {file} : {e}")

            except Exception as e:
                print(f"Erreur générale GOSAT pour la date {date} : {e}")

            date = date + timedelta(days=1)


    elif satellite == "MODIS_DEEP_BLUE":



        try:
            Dbcontroller = DeepBlueInserter(os.path.join(basePath, "satelliteData.db"))
            localDataPath = os.path.join(basePath, "data", "MODIS", "MODIS_DEEP_BLUE")
            os.makedirs(localDataPath, exist_ok=True)
        except Exception as e:
            print(f"Erreur lors de l'initialisation du contrôleur DeepBlue : {e}")
            return nbData

        while date <= end_date:
            try:
                socketio.emit('fetch_progress',
                          {'current': (date - start_date).days + 1, 'total': (end_date - start_date).days + 1})
            except Exception as e:
                print(f"Erreur lors de l'émission du progrès via SocketIO : {e}")

            try:
                file, foundLocally = find_file_by_date(localDataPath, "MODIS_DEEP_BLUE", date)

                if file == "" and not localOnly:
                    try:
                        file = handle_modis_fetch("MODIS_DEEP_BLUE", date, basePath)
                    except Exception as e:
                        print(f"Erreur lors du téléchargement MODIS pour {date} : {e}")
                        file = ""

                if file != "":
                    try:
                        data = Dbcontroller.process_file(lat, long, radius, date, file)
                        nbData += len(data)
                        Dbcontroller.insert_data(data)
                    except Exception as e:
                        print(f"Erreur lors du traitement/insertion MODIS pour {file} : {e}")

                    if not keepOption and not localOnly and not foundLocally:
                        try:
                            os.remove(file)
                        except Exception as e:
                            print(f"Erreur lors de la suppression du fichier {file} : {e}")

            except Exception as e:
                print(f"Erreur générale MODIS pour la date {date} : {e}")

            date = date + timedelta(days=1)
            socketio.emit('fetch_progress',
                          {'current': (date - start_date).days + 1, 'total': (end_date - start_date).days + 1})

    return nbData