
from flask import Flask, request, jsonify
from os import environ
import datetime
import math
import requests

from google.cloud import secretmanager

app = Flask(__name__)

# from google.cloud import secretmanager

# GCP project in which to store secrets in Secret Manager.
project_id = "the-co2-shifter"

# ID of the secret to create.
secret_id = "electricity_maps_token"

# Create the Secret Manager client.
client = secretmanager.SecretManagerServiceClient()


def stringToDatetime(stringDateTime):
    stringDateTime = stringDateTime.replace('Z', '+00:00')
    return datetime.datetime.strptime(stringDateTime, "%Y-%m-%dT%H:%M:%S.%f%z")


@app.route('/', methods=["POST"])
def optimization():
    inputs = request.get_json(force=True)

    dt_earliest_start_time = stringToDatetime(inputs["earliest_start_time"])
    int_duration = inputs["duration"]
    dt_latest_end_time = stringToDatetime(inputs["latest_end_time"])

    data = forecastFromEmap()

    int_steps = int(math.ceil(int_duration / 60))

    forecast_data = data["forecast"]

    data_for_optimisation = []
    for forecastPoint in forecast_data:
        if stringToDatetime(forecastPoint["datetime"]) >= dt_earliest_start_time:
            data_for_optimisation.append(forecastPoint)
        if stringToDatetime(forecastPoint["datetime"]) > dt_latest_end_time:
            data_for_optimisation.remove(forecastPoint)

    list_total_co2 = []
    if len(data_for_optimisation) < int_steps:
        raise Exception("invalid duration or end/startdate")

    for i in range(len(data_for_optimisation) - int_steps + 1):
        list_co2 = data_for_optimisation[i:i + int_steps]
        total_co2 = 0
        for j in list_co2:
            total_co2 += j["carbonIntensity"]
        list_total_co2.append((total_co2, data_for_optimisation[i]["datetime"]))
    lowest_co2 = float('inf')
    optimal_starttime = None
    for i, entry in enumerate(list_total_co2):
        if entry[0] < lowest_co2:
            lowest_co2 = entry[0]
            optimal_starttime = entry[1]

    endtime_calculated = stringToDatetime(optimal_starttime) + datetime.timedelta(minutes=int_duration)
    endtime_calculated = endtime_calculated.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    obj_opt = [{"opt_starttime": optimal_starttime, "tot_co2": lowest_co2, "endtime": endtime_calculated}]
    return jsonify({"opt": obj_opt, "data": data_for_optimisation})


# GET FORECAST
@app.route('/forecast', methods=["GET"])
def forecast():
    return forecastFromEmap()


def forecastFromEmap():
    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": secret_name})
    token = response.payload.data.decode("UTF-8")

    url = "https://api.electricitymap.org/v3/carbon-intensity/forecast?zone=CH"
    headers = {
        "auth-token": token
    }
    response = requests.get(url, headers=headers)

    return response.json()


PORT = int(environ.get("PORT", 8082))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=PORT)
