from flask import Flask, request, jsonify
from os import environ
import datetime
import math
import requests

# From google.cloud import secretmanager
from google.cloud import secretmanager

#  Create a Flask app
app = Flask(__name__)
app.json.sort_keys = False

# GCP project in which to store secrets in Secret Manager.
project_id = "the-co2-shifter"

# ID of the secret to create.
secret_id = "electricity_maps_token"

# Create the Secret Manager client.
client = secretmanager.SecretManagerServiceClient()


# Function to convert a string to a datetime object
def stringToDatetime(stringDateTime):
    stringDateTime = stringDateTime.replace('Z', '+00:00')
    return datetime.datetime.strptime(stringDateTime, "%Y-%m-%dT%H:%M:%S.%f%z")


@app.route('/', methods=["POST"])
def optimization():
    # Inputs from the request
    inputs = request.get_json(force=True)

    dt_earliest_start_time = stringToDatetime(inputs["earliest_start_time"])
    int_duration = inputs["duration"]
    dt_latest_end_time = stringToDatetime(inputs["latest_end_time"])

    # Get the forecast data from the Electricity Map API
    data = forecastFromEmap()

    # Get hours to know how many steps we need to calculate
    int_steps = int(math.ceil(int_duration / 60))

    forecast_data = data["forecast"]

    # Filter the forecast data to only include the data we need
    data_for_optimisation = []
    for forecastPoint in forecast_data:
        if stringToDatetime(forecastPoint["datetime"]) >= dt_earliest_start_time:
            data_for_optimisation.append(forecastPoint)
        if stringToDatetime(forecastPoint["datetime"]) > dt_latest_end_time:
            data_for_optimisation.remove(forecastPoint)

    # Error handling if time is too short
    if len(data_for_optimisation) < int_steps:
        raise Exception("invalid duration or end/startdate")

    # Create groups for steps needed and calculate the total co2 for each group
    list_total_co2 = []
    first_entry = 0
    for i in range(len(data_for_optimisation) - int_steps + 1):
        list_co2 = data_for_optimisation[i:i + int_steps]
        total_co2 = 0
        for j in list_co2:
            total_co2 += j["carbonIntensity"]
        list_total_co2.append((total_co2, data_for_optimisation[i]["datetime"]))
        if first_entry == 0:
            first_entry = total_co2
    lowest_co2 = float('inf')

    # Sort the data by total
    sorted_data = sorted(list_total_co2, key=lambda pair: pair[0])

    # Get the three entries with the lowest total
    lowest_total_entries = sorted_data[:3]
    print(lowest_total_entries)

    top_3 = []
    for index, entry in enumerate(lowest_total_entries):
        percentage_saved = 100 - (entry[0] / first_entry * 100)
        percentage_saved = round(percentage_saved, 2)

        fixed_saved = first_entry - entry[0]

        average_save = (entry[0] / int_steps) * (int_duration/60)

        endtime_calculated = stringToDatetime(entry[1]) + datetime.timedelta(minutes=int_duration)
        endtime_calculated = endtime_calculated.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        top_3.append(
            {"ranking": index + 1,  "tot_co2": entry[0], "percentage_saved": percentage_saved,
             "fixed_saved": fixed_saved, "average_save": average_save, "opt_starttime": entry[1], "endtime_calculated": endtime_calculated})

    return jsonify({"opt": top_3, "data": data})


# GET FORECAST
@app.route('/forecast', methods=["GET"])
def forecast():
    return forecastFromEmap()


#  Function to get the forecast from the Electricity Map API
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
