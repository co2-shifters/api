from flask import Flask, request, jsonify
from os import environ
import logging
import json
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

    #return jsonify({"new_input1": input1, "new_input2": input2, "new_input3": input3, "token": token[:4]})
    return forecast

def api(time_window):
    print(time_window)
    return jsonify({"new_input1": 2})


PORT = int(environ.get("PORT", 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=PORT)
