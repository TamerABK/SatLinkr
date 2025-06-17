from datetime import datetime
import paramiko
import configparser
import os

data_paths = {
    "CLDD": "/pub/releaseData/standardProduct/CAI-2_L2/CLDD/0105",
    "AERP": "/pub/releaseData/standardProduct/CAI-2_L2/AERP/",
    "SWPR": "/pub/releaseData/standardProduct/FTS-2_L2/SWPR/0210",
    "SWFP": "/pub/releaseData/standardProduct/FTS-2_L2/SWFP/0210",
    "TCAP": "/pub/releaseData/standardProduct/FTS-2_L2/TCAP/"
}


class InvalidTypeError(Exception):
    """Custom exception for invalid type requests."""
    pass


def match_date_YYYYMMDD(filenames, targetDate):
    for filename in filenames:
        if filename[11:19] == targetDate:
            return filename
    return None


def match_date_YYYYMMDDHH(filenames, targetDate):
    for filename in filenames:
        if filename[11:21] == targetDate:
            return filename
    return None


class gosatDataFetcher(object):
    def __init__(self, basePath):
        self.basePath=basePath
        self.config_path = os.path.join(basePath, "auth_config.cfg")
        self.creds = self._read_sftp_credentials()
        self.transport = None
        self.sftp = None

    def _read_sftp_credentials(self):
        config = configparser.ConfigParser()
        config.read(self.config_path)
        return {
            "host": config.get("SFTP", "host"),
            "port": config.getint("SFTP", "port"),
            "username": config.get("SFTP", "username"),
            "password": config.get("SFTP", "password")
        }

    def connect(self):
        if self.sftp is None:
            self.transport = paramiko.Transport((self.creds["host"], self.creds["port"]))
            self.transport.connect(username=self.creds["username"], password=self.creds["password"])
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)

    def close(self):
        if self.sftp:
            self.sftp.close()
        if self.transport:
            self.transport.close()
        self.sftp = None
        self.transport = None

    def list_files(self, remote_path):
        try:
            self.connect()
            return self.sftp.listdir(remote_path)
        except Exception as e:
            print(f"Error listing files: {e}")
            return []

    def download_file(self, remote_path, local_path):
        try:
            self.connect()
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            # Obtenir la taille du fichier
            file_size = self.sftp.stat(remote_path).st_size
            downloaded = 0

            def download_progress(bytes_transferred, _):
                nonlocal downloaded
                downloaded = bytes_transferred  # Utiliser la valeur absolue au lieu d'accumuler
                percentage = min(100, int((downloaded / file_size) * 100))
                print(f"Downloaded : {percentage}% ({downloaded:,}/{file_size:,} bytes)")

            print(f" Starting to download {os.path.basename(remote_path)}")
            print(f"Total size : {file_size / 1024 / 1024:.2f} Mo")

            self.sftp.get(remote_path, local_path, callback=download_progress)
            print(f"Download done : {local_path}")
            return local_path

        except Exception as e:
            print(f"Error while downloading : {e}")
            return ""

        except Exception as e:
            print(f"Error while downloading : {e}")
            return ""


    def handle_gosat_fetch(self,type: str, targetDate: datetime):
        if type not in data_paths:
            raise InvalidTypeError(f"Invalid type: '{type}'. Available types: {list(data_paths.keys())}")



        local_path = os.path.join(self.basePath, "data", "GOSAT", type)
        path = data_paths[type]

        try:
            if type in ("CLDD", "AERP"):
                path = f"{path}/{targetDate.year}/{targetDate.month:02d}.{targetDate.day:02d}"
                filename = match_date_YYYYMMDDHH(
                    self.list_files(path),
                    f"{targetDate.year}{targetDate.month:02d}{targetDate.day:02d}{targetDate.hour:02d}"
                )
            else:
                path = f"{path}/{targetDate.year}"
                filename = match_date_YYYYMMDD(
                    self.list_files(path),
                    f"{targetDate.year}{targetDate.month:02d}{targetDate.day:02d}"
                )

            if filename is None:
                return ""



            os.makedirs(local_path, exist_ok=True)
            print(" Downloading: "+ filename)
            return self.download_file(
                f'{path}/{filename}',
                os.path.join(local_path, filename)
            )
        finally:
            self.close()



