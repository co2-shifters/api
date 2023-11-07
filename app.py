from flask import Flask, request, jsonify
from os import environ
import logging
# from google.cloud import secretmanager

app = Flask(__name__)

# GCP project in which to store secrets in Secret Manager.
project_id = "the-co2-shifter"

# ID of the secret to create.
secret_id = "electricity_maps_token"

# Create the Secret Manager client.
# client = secretmanager.SecretManagerServiceClient()

@app.route('/', methods=["POST"])
def hello_world():
    inputs = request.get_json(force=True)
    input1 = inputs.get("input1", "missing1")
    input2 = inputs.get("input2", "missing2")
    input3 = inputs.get("input3", "missing3")
    logging.info(input1)
    logging.info(input2)
    logging.info(input3)
    
#    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
#    response = client.access_secret_version(request={"name": secret_name})
#    token = response.payload.data.decode("UTF-8")

    return jsonify({"new_input1": input1, "new_input2": input2, "new_input3": input3, "token": token[:4]})

PORT = int(environ.get("PORT", 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=PORT)
