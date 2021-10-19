from datetime import datetime, timedelta
from xml.etree import ElementTree
from flask import Flask, jsonify, request, send_file
from flask.helpers import make_response
from flask.wrappers import Response
from flask_cors import CORS
import requests
import pandas as pd
import copy
import pyproj

app = Flask(__name__)
CORS(app)


@app.route('/')
def hello():
    return '<h1>Welcome to our demo python server :) </h1>'


tettsted_time_layer_dict = {
    2021: 'layer_293',
    2020: 'layer_273',
    2019: 'layer_233',
    2018: 'layer_212',
    2017: 'layer_198',
    2016: 'layer_166',
    2015: 'layer_140',
    2014: 'layer_40',
    2013: 'layer_39',
    2012: 'layer_38',
    2011: 'layer_13',
    2009: 'layer_48',
    2008: 'layer_49',
    2007: 'layer_50',
    2006: 'layer_51',
    2005: 'layer_52',
    2004: 'layer_53',
    2003: 'layer_54'
}

boliger_1km_layer_dict = {
    2021: 'layer_289',
    2020: 'layer_261',
    2019: 'layer_222',
    2018: 'layer_205',
    2017: 'layer_190',
    2016: 'layer_155',
    2015: 'layer_154',
    2014: 'layer_121',
    2013: 'layer_44',
    2012: 'layer_74',
    2011: 'layer_75',
    2010: 'layer_76',
    2009: 'layer_77',
    2008: 'layer_78',
}

befolkning_1km_layer_dict = {
    2019: 'layer_225',
    2018: 'layer_208',
    2017: 'layer_181',
    2016: 'layer_146',
    2015: 'layer_119',
    2014: 'layer_32',
    2013: 'layer_31',
    2012: 'layer_30',
    2011: 'layer_29',
    2010: 'layer_25',
    2009: 'layer_24',
    2008: 'layer_23',
}

landbruk_1km_layer_dict = {
    2015: 'layer_171',
    2014: 'layer_143',
    2013: 'layer_98'
}

layer_dict_dict = {
    'layer_tettsted': tettsted_time_layer_dict,
    'layer_bolig': boliger_1km_layer_dict,
    'layer_befolkning': befolkning_1km_layer_dict,
    'layer_landbruk': landbruk_1km_layer_dict
}


@app.route('/ssb_tettsteder')
def ssb_tettsteder():

    ssb_path = 'https://ogc.ssb.no/wms.ashx'
    #request.url.replace(request.host_url + 'ssb_tettsteder', ssb_path)

    params = request.args.to_dict()

    if 'request' in params:

        # Fetching the get_capabilities file
        if params['request'] == 'GetCapabilities' and params['service'] == 'WMS':
            xml_string = open('ssb_wms_getcapabilities.xml').read()
            return Response(xml_string, mimetype='text/xml')

        # Fetching stylesheet or metadata. These requests do not have a time parameter. We use 2015 because that is a value which all 
        # the layers have in common.
        elif params['request'] == 'GetLegendGraphic' or params['request'] == 'GetMetadata':
            params['layer'] = layer_dict_dict[params['layer']][2015]

        # Fetching map images
        elif params['request'] == 'GetMap':
            params['layers'] = layer_dict_dict[params['layers']][int(params['time'])]
            del params['time']

    resp = requests.get(
        url=ssb_path,
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
        params=params
    )

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    response = Response(resp.content, resp.status_code, headers)
    return response

@app.route('/proj')
def proj():
    fr = request.args.get("from")
    to = request.args.get("to")
    print(fr, to)
    if fr == None:
        fr = "epsg:5972"
    if to == None:
        to = "epsg:4326"
    points = request.args.get("points")
    points = [float(x) for x in points.split(",")]
    print(points)
    converted = []
    for i in range(0, len(points), 3):
        x = points[i]
        y = points[i+1]
        z = points[i+2]
        converted.append(pyproj.transform(fr, to,x,y,z))
    return make_response({"points": converted})

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

    data_fields = ['time', 'temperature', 'wind speed',
                   'latitude', 'longitude', 'height']
    data_dict = {field: [] for field in data_fields}

    for params in all_coords:
        response = requests.get(request_core, params, headers=headers)
        data = response.json()
        timeseries = data['properties']['timeseries']

        new_time_data = [t['time'] for t in timeseries]
        data_dict['time'] += new_time_data
        data_dict['temperature'] += [t['data']['instant']
                                     ['details']['air_temperature'] for t in timeseries]
        data_dict['wind speed'] += [t['data']['instant']
                                    ['details']['wind_speed'] for t in timeseries]
        data_dict['latitude'] += [params['lat'], ]*len(new_time_data)
        data_dict['longitude'] += [params['lon'], ]*len(new_time_data)
        data_dict['height'] += [params['altitude'], ]*len(new_time_data)

    data_frame = pd.DataFrame(data_dict)

    response = make_response(data_frame.to_csv(index=False))
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename="yr_weather.csv"'
    return response


@app.route("/sehavniva")
def sehavniva_data():
    currentDate = datetime.now()

    params = {
        'lat': 58.97,
        'lon': 5.7331,
        'fromtime': currentDate.strftime("%Y-%m-%dT00:00:00.0000z"),
        'totime': (currentDate + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00.0000z"),
        'datatype': "all",
        'refcode': "msl",
        'place': "",
        'file': "",
        'lang': "no",
        'interval': 10,
        'dst': 0,
        'tzone': "",
        'tide_request': "locationdata"
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
    data = {
        "type": "FeatureCollection",
        "features": [
        ]
    }

    # We use XPath to traverse the xml data
    # We want to return all <data> tags and their children
    for dataLevel in xmlDOM.findall("./locationdata/data"):
        if not dataLevel.attrib["type"] == "observation":
            continue
        for waterlevel in dataLevel:
            wLevel = float(waterlevel.attrib['value'])/100
            wLevel += 44.06
            coordinates = [
                [
                    [
                        5.696969032287598,
                        58.981801744181624,
                        wLevel
                    ],
                    [
                        5.715079307556152,
                        58.981801744181624,
                        wLevel
                    ],
                    [
                        5.715079307556152,
                        58.99531118795094,
                        wLevel
                    ],
                    [
                        5.696969032287598,
                        58.99531118795094,
                        wLevel
                    ],
                    [
                        5.696969032287598,
                        58.981801744181624,
                        wLevel
                    ]
                ],
                [
                    [
                        5.715165138244629,
                        58.97027804881111,
                        wLevel
                    ],
                    [
                        5.732760429382324,
                        58.97027804881111,
                        wLevel
                    ],
                    [
                        5.732760429382324,
                        58.99531118795094,
                        wLevel
                    ],
                    [
                        5.715165138244629,
                        58.99531118795094,
                        wLevel
                    ],
                    [
                        5.715165138244629,
                        58.97027804881111,
                        wLevel
                    ]
                ],
                [
                    [
                        5.732760429382324,
                        58.971406258246624,
                        wLevel
                    ],
                    [
                        5.747652053833008,
                        58.971406258246624,
                        wLevel
                    ],
                    [
                        5.747652053833008,
                        58.99533329399041,
                        wLevel
                    ],
                    [
                        5.732760429382324,
                        58.99533329399041,
                        wLevel
                    ],
                    [
                        5.732760429382324,
                        58.971406258246624,
                        wLevel
                    ]
                ],
                [
                    [
                        5.747737884521484,
                        58.96932678470925,
                        wLevel
                    ],
                    [
                        5.763959884643555,
                        58.96932678470925,
                        wLevel
                    ],
                    [
                        5.763959884643555,
                        58.990071656325064,
                        wLevel
                    ],
                    [
                        5.747737884521484,
                        58.990071656325064,
                        wLevel
                    ],
                    [
                        5.747737884521484,
                        58.96932678470925,
                        wLevel
                    ]
                ],
                [
                    [
                        5.7424163818359375,
                        58.99009376572819,
                        wLevel
                    ],
                    [
                        5.764946937561035,
                        58.99009376572819,
                        wLevel
                    ],
                    [
                        5.764946937561035,
                        59.005235372380746,
                        wLevel
                    ],
                    [
                        5.7424163818359375,
                        59.005235372380746,
                        wLevel
                    ],
                    [
                        5.7424163818359375,
                        58.99009376572819,
                        wLevel
                    ]
                ]
            ]
            props = {
                "flag": waterlevel.attrib["flag"],
                "time": waterlevel.attrib["time"],
                "value": float(waterlevel.attrib["value"])/100,
                "fill": "#00f",
                "fill-opacity": 0.5
                # f"rgb({int(255 - (float(waterlevel.attrib['value']) - minWaterLevel)/(maxWaterLevel - minWaterLevel) * 255)}, {int(255 - (float(waterlevel.attrib['value']) - minWaterLevel)/(maxWaterLevel - minWaterLevel) * 255)}, {255})"
            }

            for coordinate in coordinates:
                data["features"].append(makePolygon(coordinate, props))

    out = make_response(jsonify(data))
    out.headers['Content-Type'] = "application/json"

    return out


def makePolygon(coordinates, properties):
    return {
        "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        coordinates
                    ]
                },
        "properties": properties
    }




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
