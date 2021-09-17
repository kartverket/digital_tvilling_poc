from datetime import datetime, timedelta
from xml.etree import ElementTree
from flask import Flask, jsonify
from flask.helpers import make_response
from flask.wrappers import Response
from flask_cors import CORS
import requests
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return 'Hello, World!'


@app.route('/yr_weather') 
def yr_weather():
    
    stavanger_coords = {
        'lat': 58.97,
        'lon': 5.7331,
        'altitude': 10
    }

    oslo_coords = {
        'lat': 59.94,
        'lon': 10.7522,
        'altitude': 10
    }

    tromso_coords = {
        'lat': 69.6598,
        'lon': 18.9841,
        'altitude': 10
    }

    all_coords = [stavanger_coords, oslo_coords, tromso_coords]

    request_core = 'https://api.met.no/weatherapi/locationforecast/2.0/compact'

    headers = {
        'User-Agent': 'Digital tvilling POC',
        'From': 'https://kartverket.no/'
    }
    
    data_fields = ['time', 'temperature', 'wind speed', 'latitude', 'longitude', 'height']
    data_dict = {field : [] for field in data_fields}

    for params in all_coords:
        response = requests.get(request_core, params, headers=headers) 
        data = response.json()
        timeseries = data['properties']['timeseries']

        new_time_data = [t['time'] for t in timeseries]
        data_dict['time'] += new_time_data
        data_dict['temperature'] += [t['data']['instant']['details']['air_temperature'] for t in timeseries]
        data_dict['wind speed'] += [t['data']['instant']['details']['wind_speed'] for t in timeseries]
        data_dict['latitude'] += [params['lat'],]*len(new_time_data)
        data_dict['longitude'] += [params['lon'],]*len(new_time_data)
        data_dict['height'] += [params['altitude'],]*len(new_time_data)
    
    data_frame = pd.DataFrame(data_dict)

    response = make_response(data_frame.to_csv())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename="yr_weather.csv"'
    return response

@app.route("/sehavniva")
def sehavniva_data():
    currentDate = datetime.now()

    params = {
        'lat': 58.97,
        'lon': 5.7331,
        'fromtime':currentDate.strftime("%Y-%m-%dT%H:%M:%S.%fz"),
        'totime':(currentDate + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.%fz"),
        'datatype':"all",
        'refcode':"cd",
        'place':"",
        'file':"",
        'lang':"no",
        'interval':10,
        'dst':0,
        'tzone':"",
        'tide_request':"locationdata"
    }
    
    request_core = "http://api.sehavniva.no/tideapi.php"
    
    headers = {
        'User-Agent': 'Digital tvilling POC',
        'From': 'https://kartverket.no/'
    }


    response = requests.get(request_core, params, headers=headers)
    
    # We use the included ElementTree library to parse and traverse the XML output
    # As we receive the XML data in the form of a text response, we need to use the fromstring
    # function to parse the data.
    xmlDOM = ElementTree.fromstring(response.text)
    data = {}

    # We use XPath to traverse the xml data
    # We want to return all <data> tags and their children
    for dataLevel in xmlDOM.findall("./locationdata/data"):
        data[dataLevel.attrib["type"]] = []
        for waterlevel in dataLevel:
            data[dataLevel.attrib["type"]].append(waterlevel.attrib)

    out = make_response(jsonify(data))
    out.headers['Content-Type'] = "application/json"

    return out


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)