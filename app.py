from flask import Flask, request, jsonify
from os import environ
import logging
import json
import datetime
import math 
# from google.cloud import secretmanager

app = Flask(__name__)

# GCP project in which to store secrets in Secret Manager.
project_id = "the-co2-shifter"

# ID of the secret to create.
secret_id = "electricity_maps_token"

# Create the Secret Manager client.
# client = secretmanager.SecretManagerServiceClient()

@app.route('/', methods=["POST"])
def optimization():
    inputs = request.get_json(force=True)
    logging.info(inputs)
    logging.info("=====")
    print("=====>")
    print(inputs)

    dt_earliest_start_time = inputs["earliest_start_time"]
    int_duration = inputs["duration"]
    dt_latest_end_time= inputs["latest_end_time"]
    print(dt_earliest_start_time)
    print(int_duration)
    print(dt_latest_end_time)

    forecast = api(json.dumps({"earliest_start_time": dt_earliest_start_time, "latest_end_time": dt_latest_end_time}))
    print(forecast)

    data = forecast["forecast"]
    dt_earliest_start_time = dt_earliest_start_time.replace('Z', '+00:00')
    dt_earliest_start_datetime = datetime.datetime.strptime(dt_earliest_start_time, "%Y-%m-%dT%H:%M:%S.%f%z")
    end_time = dt_earliest_start_datetime + datetime.timedelta(minutes=int_duration)
    int_steps = int(math.ceil(int_duration/60))
    print(end_time)

    int_steps = 2
    list_total_co2 = []
    for i in range(len(data) - int_steps + 1):
        list_co2 = data[i:i + int_steps]
        total_co2 = 0
        for j in list_co2: 
            total_co2 += j["carbonIntensity"]
        list_total_co2.append((total_co2, data[i]["datetime"]))     
    lowest_co2 = float('inf')
    optimal_starttime = None
    for i, entry in enumerate(list_total_co2):
        if entry[0] < lowest_co2:
            lowest_co2 = entry[0]
            optimal_starttime = entry[1]

    return jsonify([{"opt_starttime": optimal_starttime, "tot_co2": lowest_co2}])

def api(time_window):
    print(time_window)

    obj = {
    "forecast": [
      {
        "carbonIntensity": 74,
        "datetime": "2023-11-06T09:00:00.000Z"
      },
      {
        "carbonIntensity": 79,
        "datetime": "2023-11-06T10:00:00.000Z"
      },
      {
        "carbonIntensity": 81,
        "datetime": "2023-11-06T11:00:00.000Z"
      },
      {
        "carbonIntensity": 73,
        "datetime": "2023-11-06T12:00:00.000Z"
      },
      {
        "carbonIntensity": 75,
        "datetime": "2023-11-06T13:00:00.000Z"
      },
     ]
    }
    return obj


PORT = int(environ.get("PORT", 8082))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=PORT)
