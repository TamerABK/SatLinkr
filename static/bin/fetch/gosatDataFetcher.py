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
    # Iterate over filenames to find the first match for YYYYMMDD (12th to 19th characters)
    for filename in filenames:
        if filename[11:19]==targetDate:
            return filename  # Return the first matching filename
    return None  # Return None if no match is found

def match_date_YYYYMMDDHH(filenames, targetDate):
    # Iterate over filenames to find the first match for YYYYMMDDHH (12th to 21st characters)
    for filename in filenames:
        if filename[11:21]==targetDate:
            return filename  # Return the first matching filename
    return None  # Return None if no match is found

# Read SFTP credentials from config file
def read_sftp_credentials(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)

    return {
        "host": config.get("SFTP", "host"),
        "port": config.getint("SFTP", "port"),
        "username": config.get("SFTP", "username"),
        "password": config.get("SFTP", "password")
    }

# Connect to SFTP server
def connect_sftp(creds):
    
    transport = paramiko.Transport((creds["host"], creds["port"]))
    transport.connect(username=creds["username"], password=creds["password"])
    return paramiko.SFTPClient.from_transport(transport)

# List files in a remote directory
def list_files(remote_path,creds):
    try:
        sftp = connect_sftp(creds)
        files = sftp.listdir(remote_path)
        sftp.close()
        return files
    except Exception as e:
        print(f"Error listing files: {e}")
        return []

# Download a file from SFTP
def download_file(remote_path, local_path,creds):
    try:
        sftp = connect_sftp(creds)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        sftp.get(remote_path, local_path)
        sftp.close()
        return local_path
    except Exception as e:
        print(f"Error downloading file: {e}")
        return ""



def handle_gosat_fetch(type:str,targetDate:datetime,basePath):
    
    if type not in data_paths:
        raise InvalidTypeError(f"Invalid type: '{type}'. Available types: {list(data_paths.keys())}")
    
    
    # Define the SFTP config file name
    config_file_path = os.path.join(basePath, "sftp_config.cfg")
    creds=read_sftp_credentials(config_file_path)
    local_path=os.path.join(basePath,"data","GOSAT",type)
    path=data_paths[type]

    if type in ("CLDD","AERP"):
        path = f"{path}/{targetDate.year}/"+f"{targetDate.month:02d}.{targetDate.day:02d}"
        filename= match_date_YYYYMMDDHH(list_files(path,creds),f"{targetDate.year}{targetDate.month:02d}{targetDate.day:02d}{targetDate.hour:02d}")
        
    else:
        path = f"{path}/{targetDate.year}" 
        filename= match_date_YYYYMMDD(list_files(path,creds),f"{targetDate.year}{targetDate.month:02d}{targetDate.day:02d}")
    
    if (filename==None): 
        return ""

    return download_file(f'{path}/{filename}',os.path.join(local_path,filename),creds)
    


# Example usage
if __name__ == "__main__":
    # Example: List files in one of the given folders
    handle_gosat_fetch("SWPR",datetime(day=1,month=1,year=2024),"./") 

