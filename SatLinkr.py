import glob
import shutil
from threading import Timer
import webbrowser
from flask import Flask, jsonify, render_template, request
import sys
import numpy as np
from flask_socketio import SocketIO, emit

from static.bin.db.TCCONInserter import TCCONInserter
from static.bin.filter.filterTCCON import query_tccon
from static.bin.gen.genCSV import gen_csv
from static.bin.gen.genMap import generate_map
from static.bin.gen.genPng import genPng
from static.bin.db.GOSATInserter import GOSATInserter
from static.bin.db.OCO2Inserter import OCO2Inserter
from static.bin.fetch.fetchHandler import FetchHandler
from static.bin.filter.filterDeepBlue import query_deepblue
from static.bin.filter.filterSWPR import *
from static.bin.filter.filterOCO2 import *
from static.bin.filter.filterForCSV import *
from static.bin.filter.regionQuery import get_all_regions, get_region_dates, get_region

sys.path.append(os.path.join(os.getcwd(), "static", "bin", "filter"))

GASOPTION = {
    "OCO2": ["CO2"],
    "GOSAT": ["CO2", "CH4", "CO", "H2O"],
    "MODIS_DEEP_BLUE": [
        "Aerosol_Optical_Thickness_Land_Count",
        "Aerosol_Optical_Thickness_Land_Maximum",
        "Aerosol_Optical_Thickness_Land_Mean",
        "Aerosol_Optical_Thickness_Land_Minimum",
        "Aerosol_Optical_Thickness_Land_Standard_Deviation",
        "Angstrom_Exponent_Land_Maximum",
        "Angstrom_Exponent_Land_Mean",
        "Angstrom_Exponent_Land_Minimum",
        "Angstrom_Exponent_Land_Standard_Deviation",
        "Spectral_Aerosol_Optical_Thickness_Land_Count",
        "Spectral_Aerosol_Optical_Thickness_Land_Mean",
        "Spectral_Aerosol_Optical_Thickness_Land_Standard_Deviation"
    ]
}

BANDOPTION = {
    "OCO2": {
        "CO2": []
    },
    "GOSAT": {
        "CO2": ["2060", "1590"],
        "H2O": ["1590", "1660", "2060", "2350"],
        "CH4": ["1660", "2350"],
        "CO": ["2350"],
    },
    "MODIS_DEEP_BLUE": {
        "Aerosol_Optical_Thickness_Land_Count": ["550"],
        "Aerosol_Optical_Thickness_Land_Maximum": ["550"],
        "Aerosol_Optical_Thickness_Land_Mean": ["550"],
        "Aerosol_Optical_Thickness_Land_Minimum": ["550"],
        "Aerosol_Optical_Thickness_Land_Standard_Deviation": ["550"],
        "Angstrom_Exponent_Land_Maximum": ["None"],
        "Angstrom_Exponent_Land_Mean": ["None"],
        "Angstrom_Exponent_Land_Minimum": ["None"],
        "Angstrom_Exponent_Land_Standard_Deviation": ["None"],
        "Spectral_Aerosol_Optical_Thickness_Land_Count": ["412", "488", "670"],
        "Spectral_Aerosol_Optical_Thickness_Land_Mean": ["412", "488", "670"],
        "Spectral_Aerosol_Optical_Thickness_Land_Standard_Deviation": ["412", "488", "670"]
    }
}
app = Flask(__name__)
app.secret_key = os.urandom(24)
socketio = SocketIO(app)


def clean_tmp_directory():
    tmp_path = os.path.join(os.getcwd(), 'tmp')
    # Crée le dossier tmp s'il n'existe pas
    os.makedirs(tmp_path, exist_ok=True)
    # Supprime tous les fichiers dans tmp
    files = glob.glob(os.path.join(tmp_path, '*'))
    for f in files:
        try:
            if os.path.isfile(f):
                os.unlink(f)
            elif os.path.isdir(f):
                shutil.rmtree(f)
        except Exception as e:
            print(f'Erreur lors de la suppression de {f}: {e}')

def get_data(satellite, field, band, lat, long, radius, date, delta, satellite_criteria):


    if field == "*":
        return query_filter_for_csv(os.getcwd(), satellite, date, delta, lat, long, radius), True

    if satellite == "GOSAT":
        return query_gosat(os.getcwd(), field, band, date, delta, lat, long, radius), True

    elif satellite == "OCO2":
        return query_oco2(os.getcwd(), date, delta, lat, long, radius, satellite_criteria), True

    elif satellite == "MODIS_DEEP_BLUE":
        date = date.replace(hour=0, minute=1, second=0, microsecond=0)
        return query_deepblue(os.getcwd(), field, band, date, 15, lat, long, radius), True

    return None


@socketio.on('change_satellite')
def handle_change_satellite(data):
    satellite = data.get('satellite')
    gases = GASOPTION[satellite]
    emit('update_gases', {'satellite': satellite, 'gases': gases})


@socketio.on('change_gas')
def handle_change_gas(data):
    satellite = data.get('satellite')
    gas = data.get('gas')
    try:
        emit('update_bands', {'bands': BANDOPTION[satellite][gas]})
    except KeyError:
        emit('update_bands', {'bands': []})


@app.route('/render_map_png', methods=['POST'])
def render_map_png():
    clean_tmp_directory()
    return genPng()


@app.route('/update_map', methods=['POST'])
def update_map():
    option = request.form.get('region_option')
    region = request.form.get('existing_region')
    gas = request.form.get("gas")
    band = request.form.get("band")
    tcconOption = request.form.get("showTCCON")

    if option == "existing":
        satellite, latitude, longitude, radius = get_region(os.getcwd(), region)
    else:
        satellite = request.form.get("satellite")
        latitude = np.float64(request.form.get("latitude"))
        longitude = np.float64(request.form.get("longitude"))
        radius = int(request.form.get("radius"))

    try:
        date = datetime.strptime(request.form.get("datetime"), "%d/%m/%Y %H:%M")
    except ValueError:
        try:
            date = datetime.strptime(request.form.get("datetime"), "%d/%m/%Y")
        except ValueError:
            return jsonify({'error': "Invalid date format. Use 'dd/mm/yyyy' or 'dd/mm/yyyy HH:MM'."})

    delta_time = int(request.form.get("delta_time"))
    satellite_criteria = request.form.get("satellite_criteria")

    data, success = get_data(satellite, gas, band, latitude, longitude, radius, date, delta_time, satellite_criteria)

    if not data:
        if success:
            return jsonify({'error': "No data found within those parameters"})
        else:
            return jsonify({'error': "No file found for this date locally or on the servers"})

    if satellite == "MODIS_DEEP_BLUE":
        mode = 'squares'
        scale_title = gas.replace('_', ' ')
        if band and band != "None":
            scale_title += f" ({band} nm)"
        scale_title += " <br>MODIS Deep Blue"
    elif satellite == "GOSAT":
        mode = 'heatmap'
        scale_title = "Concentration " + gas.strip('_') + " " + band + " nm (ppm) <br>" + "GOSAT SWPR"
    elif satellite == "OCO2":
        mode = 'heatmap'
        scale_title = " Concentration CO2 (ppm) <br> OCO2"

    tccon_data = []
    if tcconOption:
        tccon_data=query_tccon(os.getcwd(),gas,date,delta_time,latitude,longitude,radius)
        print(tccon_data)

    map_html = generate_map(latitude, longitude, radius, data, scale_title,tccon_data, mode)
    return jsonify({'map_html': map_html})


@app.route('/launch_csv', methods=['POST'])
def launch_csv():
    clean_tmp_directory()
    option = request.form.get('region_option')
    region = request.form.get('existing_region')
    allDatesOption = request.form.get('allCsvDates')

    if option == "existing":
        satellite, latitude, longitude, radius = get_region(os.getcwd(), region)
    else:
        satellite = request.form.get("satellite")
        latitude = np.float64(request.form.get("latitude"))
        longitude = np.float64(request.form.get("longitude"))
        radius = int(request.form.get("radius"))

    date = None
    csvName = f'{satellite}_all.csv'

    if not allDatesOption:

        try:
            date = datetime.strptime(request.form.get("datetime"), "%d/%m/%Y %H:%M")
        except ValueError:
            try:
                date = datetime.strptime(request.form.get("datetime"), "%d/%m/%Y")
            except ValueError:
                return jsonify({'error': "Invalid date format. Use 'dd/mm/yyyy' or 'dd/mm/yyyy HH:MM'."})

        csvName = f"{satellite}_{date.strftime('%Y-%m-%d_%H-%M')}.csv"

    delta_time = int(request.form.get("delta_time"))

    satellite_criteria = request.form.get("satellite_criteria")

    data, success = get_data(satellite, "*", 0, latitude, longitude, radius, date, delta_time, satellite_criteria)
    header,data=data[0],data[1]

    if not data:
        if success:
            return jsonify({'error': "No valid data found within those parameters"})
        else:
            return jsonify({'error': "No file found for this date locally or on the servers"})



    return gen_csv(data, header,csvName)

@app.route('/upload_tccon', methods=['POST'])
def upload_tccon():
    file = request.files.get('tcconFile')
    station = request.form.get('station_name')
    inserter = TCCONInserter(os.path.join(os.getcwd(), 'satelliteData.db'))

    if not file or not file.filename.endswith('.nc'):
        return jsonify({'error': 'Fichier non valide'}), 400
    filepath = os.path.join(os.getcwd(), 'tmp', file.filename)
    file.save(filepath)
    rows = inserter.process_file(filepath)
    lat,long= rows[0][2],rows[0][3]

    try:
        inserter.insert_data(rows)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    inserter.add_station(station,lat,long)



    return jsonify({'success': f'Fichier {file.filename} uploadé'})

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
            d.strftime("%d/%m/%Y") for d in get_region_dates(base_path, (region["name"],))
        ]
        region_data.append(region)
    return jsonify(region_data)


@app.route('/fetchData', methods=['POST'])
def fetch_data():
    print("Fetching data")
    handler = FetchHandler(os.getcwd())
    option = request.form.get("region_option")
    print(request.form.get("datetime_start"))
    date_start = datetime.strptime(request.form.get("datetime_start"), "%d/%m/%Y")
    date_end = datetime.strptime(request.form.get("datetime_end"), "%d/%m/%Y")
    localOnly = request.form.get("source") == "local"
    keepOption = bool(request.form.get("keepOption"))

    if option == "existing":
        region_name = request.form.get("existing_region")
        satellite, lat, long, radius = get_region(os.getcwd(), region_name)

        try:
            handler.register_fetch(region_name, satellite, lat, long, radius, date_start, date_end, localOnly,
                                   keepOption, socketio)
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
            handler.register_fetch(region_name, satellite, lat, long, radius, date_start, date_end, localOnly,
                                   keepOption, socketio)
        except Exception as e:
            handler.close()
            return jsonify({'error': str(e)})

    handler.close()
    return "200"


# Route for the main page
@app.route('/', methods=['GET', 'POST'])
def index():
    gas = "CO2"
    satellite = "OCO2"
    latitude = 48.8566
    longitude = 2.3522
    radius = 10
    band = "1590"
    date = datetime(day=24, month=3, year=2024, hour=12, minute=1)
    delta_time = 30
    satellite_criteria = "True"
    ground_criteria = "Flag"

    OCO2Inserter(os.path.join(os.getcwd(), 'satelliteData.db'))
    GOSATInserter(os.path.join(os.getcwd(), 'satelliteData.db'))

    data, success = get_data(satellite, gas, band, latitude, longitude, radius, date, delta_time, satellite_criteria)
    clean_tmp_directory()
    map_html = generate_map(latitude, longitude, radius, data, "", "")
    return render_template('UItemplate.html', map_html=map_html, selected_gas=gas, selected_band=band,
                           satellite=satellite, latitude=latitude, longitude=longitude,
                           radius=radius, datetime=date.strftime("%d/%m/%Y %H:%M"),
                           delta_time=delta_time, satellite_criteria=satellite_criteria,
                           option="existing")


if __name__ == '__main__':
    Timer(3, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    socketio.run(app, debug=False,allow_unsafe_werkzeug=True)
