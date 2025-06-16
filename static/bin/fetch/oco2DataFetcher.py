import os
import subprocess
import configparser
import sys
from datetime import datetime

def read_wget_credentials(config_path="auth_config.cfg"):
    config = configparser.ConfigParser()
    config.read(config_path)

    return {
        "username": config.get("OCO2", "username"), 
        "password": config.get("OCO2", "password"),
        "cookies": config.get("OCO2","cookies")
    }

def get_wget_path():
    if hasattr(sys, '_MEIPASS'):
        # Exécution depuis un exécutable PyInstaller
        return os.path.join(sys._MEIPASS, 'static', 'bin', 'wget.exe')
    else:
        # Exécution depuis le code source
        return os.path.join(os.getcwd(), 'static', 'bin', 'wget.exe')

def download_with_wget(url,output,creds):


    try:

        subprocess.run([get_wget_path(),"--load-cookies",creds['cookies'], "--save-cookies",creds['cookies'],"--user", creds["username"], "--password", creds["password"], url, "-O", output], check=True)
        return None
    except Exception as e:
        print(f"Error downloading file: {e}")
        return ""
    
def matchURl(targetDate:datetime,linksFile="OCO2links.txt"):
    target=f"{str(targetDate.year)[-2:]}{targetDate.month:02d}{targetDate.day:02d}"
    with open(linksFile,'r') as f:
        lines= f.readlines()
        for line in lines:  
            if line[93:99]==target:  
                return line[:-1]
    return None

def handle_oco2_fetch(targetDate:datetime,basePath): 
    linksFile = os.path.join(basePath,"OCO2links.txt")
    url = matchURl( targetDate, linksFile ) 

    if not url:
        print("No link for files of this day")
        return ""
    
    output = os.path.join(basePath,"data","OCO2",str(targetDate.year))
    os.makedirs(output,exist_ok=True)
    output=os.path.join(output,url.split('/')[-1])
    config_path = os.path.join(basePath, "auth_config.cfg")
    creds=read_wget_credentials(config_path)
    download_with_wget(url,output,creds)
    return output




if __name__ == "__main__":
    handle_oco2_fetch(datetime(year=2024,month=4,day=11),'C:\\Users\Enseignement\PycharmProjects\satelliteImageryApp\\')
        