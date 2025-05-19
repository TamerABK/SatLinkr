from threading import Timer
from datetime import datetime
import webbrowser
from flask import Flask, jsonify, render_template, request,flash
import os, uuid
import sys
import numpy as np
from flask_socketio import SocketIO, emit
from genMap import generate_map
from genPng import genPng
from static.bin.db.GOSATInserter import GOSATInserter
from static.bin.db.OCO2Inserter import OCO2Inserter
from static.bin.fetch.fetchHandler import FetchHandler
from static.bin.filter.filterSWPR import *
from static.bin.filter.filterOCO2 import *
from static.bin.filter.regionQuery import get_all_regions, get_region_dates, get_region

sys.path.append(os.path.join(os.getcwd(),"static","bin","filter"))

GASOPTION={
    "OCO2":["CO2"],
    "GOSAT":["CO2","CH4","CO","H2O"]
}

BANDOPTION={
    "CO2":["2060","1590"],
    "H2O":["1590","1660","2060","2350"],
    "CH4":["1660","2350"],
    "CO":["2350"]
}

app = Flask(__name__)
app.secret_key = os.urandom(24)
socketio = SocketIO(app)    



def get_data(satellite,gas,band,lat,long,radius,date,delta,satellite_criteria):

    
    if satellite == "GOSAT":
        return query_gosat(os.getcwd(),gas,band,date,delta,lat,long,radius),True
      
    elif satellite == "OCO2":
        return query_oco2(os.getcwd(),date,delta,lat,long,radius,satellite_criteria),True

    return None


@socketio.on('change_satellite')
def handle_change_satellite(data):
    satellite = data.get('satellite')
    gases = GASOPTION[satellite]
    emit('update_gases', {'gases': gases})

@socketio.on('change_gas')
def handle_change_gas(data):
    satellite = data.get('satellite')
    gas = data.get('gas')
    if satellite=="GOSAT": bands = BANDOPTION[gas]
    else: bands=[]
    emit('update_bands', {'bands': bands})
 

@app.route('/render_map_png', methods=['POST'])
def render_map_png():
    return genPng()

@app.route('/update_map', methods=['POST'])
def update_map():
    option= request.form.get('region_option')
    region = request.form.get('existing_region')
    gas = request.form.get("gas")
    band = request.form.get("band")

    if option == "existing":
        satellite, latitude, longitude,radius = get_region(os.getcwd(),region)
    else:
        satellite = request.form.get("satellite")
        latitude = np.float64(request.form.get("latitude"))
        longitude = np.float64(request.form.get("longitude"))
        radius = int(request.form.get("radius"))

    date = datetime.strptime(request.form.get("datetime"), "%d/%m/%Y %H:%M")
    delta_time = int(request.form.get("delta_time"))
    satellite_criteria = request.form.get("satellite_criteria")


    data, success = get_data(satellite, gas, band, latitude, longitude, radius, date, delta_time, satellite_criteria)
    print(data)
    if not data:
        if success:
            return jsonify({'error': "No data found within those parameters"})
        else:
            return jsonify({'error': "No file found for this date locally or on the servers"})

    map_html = generate_map(latitude, longitude, radius, data)
    return jsonify({'map_html': map_html})

@app.route('/regions', methods=['GET'])
def region_details():
    base_path = os.getcwd()
    region_data = []
    for row in get_all_regions(base_path):
        region = {
            "name": row[0],
            "satellite": row[1],
            "lat": row[2],
            "lon": row[3],
            "radius": row[4],
        }
        region["available_dates"] = [
            d.isoformat() for d in get_region_dates(base_path, (region["name"],))
        ]
        region_data.append(region)
    return jsonify(region_data)

@app.route('/fetchData', methods=['POST'])
def fetch_data():
    print("Fetching data")
    handler= FetchHandler(os.getcwd())
    option= request.form.get("region_option")
    print(request.form.get("datetime_start"))
    date_start = datetime.strptime(request.form.get("datetime_start"), "%d/%m/%Y")
    date_end = datetime.strptime(request.form.get("datetime_end"), "%d/%m/%Y")
    localOnly = request.form.get("source") == "local"
    keepOption = bool(request.form.get("keepOption"))


    if option == "existing":
        region_name = request.form.get("existing_region")
        satellite,lat,long,radius= get_region(os.getcwd(), region_name)

        try:
            handler.register_fetch(region_name, satellite, lat, long, radius, date_start, date_end,localOnly, keepOption)
        except Exception as e:
            handler.close()
            return jsonify({'error': str(e)})

    elif option == "new":
        print("Fetching new data")
        region_name = request.form.get("region_name")
        satellite = request.form.get("satellite_fetch")
        lat = float(request.form.get("latitude_fetch"))
        long = float(request.form.get("longitude_fetch"))
        radius = float(request.form.get("radius_fetch"))

        try:
            handler.register_fetch(region_name, satellite, lat, long, radius, date_start, date_end,localOnly, keepOption)
        except Exception as e:
            handler.close()
            return jsonify({'error': str(e)})

    handler.close()
    return "200"





# Route for the main page
@app.route('/', methods=['GET','POST'])
def index():
    gas = "CO2"
    satellite = "OCO2" 
    latitude = 48.8566 
    longitude = 2.3522
    radius = 10
    band="1590"
    date = datetime(day=24,month=3,year=2024,hour=12,minute=1)
    delta_time = 30
    satellite_criteria = "True"
    ground_criteria = "Flag" 

    OCO2Inserter(os.path.join(os.getcwd(),'satelliteData.db'))
    GOSATInserter(os.path.join(os.getcwd(), 'satelliteData.db'))


    data,success=get_data(satellite,gas,band,latitude,longitude,radius,date,delta_time,satellite_criteria)
    
    map_html = generate_map(latitude,longitude,radius,data)
    return render_template('mapTemplate.html', map_html=map_html, selected_gas=gas, selected_band=band, 
                           satellite=satellite, latitude=latitude, longitude=longitude,
                           radius=radius, datetime=date.strftime("%d/%m/%Y %H:%M"), 
                           delta_time=delta_time, satellite_criteria=satellite_criteria,
                           option="existing")

if __name__ == '__main__':
    Timer(3, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    
    socketio.run(app, debug=True)           
      