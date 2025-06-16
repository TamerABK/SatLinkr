import requests
import json
import os
import configparser
from datetime import datetime,timedelta


def download_file_by_date(data_dict, target_date, token, path):

    dayOfYear= target_date - datetime(day=1,month=1,year=target_date.year) + timedelta(days=1)
    print(f"A{target_date.year}{dayOfYear.days:03d}")
    for item in data_dict:
        if item == "query":
            continue
        url = data_dict[item]["url"]
        
        if f"A{target_date.year}{dayOfYear.days:03d}" in url:
            filename = url.split("/")[-1]
            headers = {
                "Authorization": f"Bearer {token}"
            }
            print(f"Downloading: {filename} from {url}")
            response = requests.get(url, headers=headers, stream=True)
            if response.status_code == 200:
                filePath = os.path.join(path, filename)
                with open(filePath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                print(f"Downloaded {filename} successfully.")
                return filePath
            else:
                print(f"Failed to download file. Status code: {response.status_code}")
                print(f"Response: {response.text[:200]}...")  # Show preview of the error
    return " "


def read_token(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)

    return config.get('MODIS','token')

def handle_modis_fetch(type, target_date, basePath):

    config_path = os.path.join(basePath, "auth_config.cfg")
    token = read_token(config_path)

    if type == 'TerraAqua' :
        with open(os.path.join(basePath,'OPDEPTH.json'),'r') as file:
            urls= json.load(file)
    elif type == 'MODIS_DEEP_BLUE' :
        with open(os.path.join(basePath,'DEEP.json'),'r') as file:
            urls= json.load(file)

    os.makedirs(os.path.join(basePath,'data','MODIS',type),exist_ok=True)
    return download_file_by_date(urls,target_date,token,os.path.join(basePath,'data','MODIS',type))

if __name__=='__main__':

    handle_modis_fetch('MODIS_DEEP_BLUE', datetime(year=2024,month=4,day=12), os.path.join('C:\\Users\Enseignement\PycharmProjects\satelliteImageryApp'))
    handle_modis_fetch('TerraAqua', datetime(year=2023,month=1,day=25), os.path.join('C:\\Users\Enseignement\PycharmProjects\satelliteImageryApp'))