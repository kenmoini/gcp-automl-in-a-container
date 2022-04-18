# [START aiplatform_predict_image_classification_sample]
import base64
import os
import sys, getopt
import time
import json
import proto
import string


from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
from google.oauth2.service_account import Credentials
from google.protobuf.json_format import MessageToJson
from flask_cors import CORS, cross_origin
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

# Get environs
homePath = "/root" if os.getenv("HOME") is None else os.getenv("HOME")
gcpSACredentialsJSONFile = homePath + "/gcp-service-account-file.json" if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") is None else os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
gcpLocation = "us-central1" if os.getenv('GCP_LOCATION') is None else os.getenv('GCP_LOCATION')
projectID = "" if os.getenv('GCP_PROJECT_ID') is None else os.getenv('GCP_PROJECT_ID')
endpointID = "" if os.getenv('GCP_AI_ENDPOINT_ID') is None else os.getenv('GCP_AI_ENDPOINT_ID')
apiEndpoint = (gcpLocation + "-aiplatform.googleapis.com") if os.getenv('GCP_API_ENDPOINT') is None else os.getenv('GCP_API_ENDPOINT')

credentials = Credentials.from_service_account_file(gcpSACredentialsJSONFile)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def predict_image_classification(
    project: str,
    endpoint_id: str,
    filename: str,
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
):
    print("gcpSACredentialsJSONFile: ", gcpSACredentialsJSONFile)
    print("project: ", project)
    print("endpoint_id: ", endpoint_id)
    print("filename: ", filename)
    print("location: ", location)
    print("api_endpoint: ", api_endpoint)

    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options, credentials=credentials)
    #client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
    with open(filename, "rb") as f:
        file_content = f.read()

    # The format of each instance should conform to the deployed model's prediction input schema.
    encoded_content = base64.b64encode(file_content).decode("utf-8")
    instance = predict.instance.ImageClassificationPredictionInstance(
        content=encoded_content,
    ).to_value()
    instances = [instance]
    # See gs://google-cloud-aiplatform/schema/predict/params/image_classification_1.0.0.yaml for the format of the parameters.
    parameters = predict.params.ImageClassificationPredictionParams(
        confidence_threshold=0.5, max_predictions=5,
    ).to_value()
    endpoint = client.endpoint_path(
        project=project, location=location, endpoint=endpoint_id
    )
    response = client.predict(
        endpoint=endpoint, instances=instances, parameters=parameters
    )
    #print("response")
    #print(" deployed_model_id:", response.deployed_model_id)
    # See gs://google-cloud-aiplatform/schema/predict/prediction/image_classification_1.0.0.yaml for the format of the predictions.
    return response
    #predictions = response.predictions
    #for prediction in predictions:
    #    #print(" prediction:", dict(prediction))
    #    print(dict(prediction))

def predict_image_classification_sample(response):
    print("response")
    print(" deployed_model_id:", response.deployed_model_id)
    predictions = response.predictions
    for prediction in predictions:
        print(" prediction:", dict(prediction))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def main(argv):
    mode = ''
    inputfile = ''
    port = '8080'
    try:
        opts, args = getopt.getopt(argv,"hm:f:p:",["mode=","file=","port="])
    except getopt.GetoptError:
        print ('main.py [-m server] [-p <port>] -f <inputfile>')
        sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
          print ('main.py [-m server] [-p <port>] -f <inputfile>')
          sys.exit()
      elif opt in ("-m", "--mode"):
          mode = arg.strip()
      elif opt in ("-f", "--file"):
          inputfile = arg.strip()
      elif opt in ("-p", "--port"):
          port = arg.strip()
    print ('Mode is', mode)
    print ('Input file is', inputfile)
    print ('Port is', port)

    if mode == 'server':
        ## Run an HTTP Server to respond to ase64 encoded images
        print ("Running in server mode")
        
        ## Create a flask server and listen on port 8080
        app = Flask(__name__)
        app.config['UPLOAD_FOLDER'] = '/tmp'
        # After creating the Flask app, you can make all APIs allow cross-origin access.
        CORS(app)
        # or a specific API
        @app.route("/predict", methods=['POST'])
        @cross_origin()
        def upload_file():
            print ("Received a POST predict request")
            if request.method == 'POST':
                # check if the post request has the file part
                if 'file' not in request.files:
                    print ('No file part')
                    return 'No file part'
                file = request.files['file']
                # if user does not select file, browser also
                # submit a empty part without filename
                if file.filename == '':
                    print ('No selected file')
                    return 'No selected file'
                if file and allowed_file(file.filename):
                    now = int( time.time() )
                    filename = str(now) + secure_filename(file.filename)
                    print ("Filename: ", filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    # Call predict_image_classification
                    predictionCall = predict_image_classification(
                        project=projectID,
                        endpoint_id=endpointID,
                        filename=os.path.join(app.config['UPLOAD_FOLDER'], filename),
                        location=gcpLocation,
                        api_endpoint=apiEndpoint,
                    )
                    
                    predictionJSON = {"deployed_model_id": predictionCall.deployed_model_id, "model_name": predictionCall.model_display_name,  "data": []}

                    predictions = predictionCall.predictions
                    for prediction in predictions:
                        d = dict(prediction)
                        objJSON = {"id": d['ids'][0], "confidences": d['confidences'][0], "display_names": d['displayNames'][0]}
                        predictionJSON["data"].append(objJSON)

                    jsonObj = {
                        "project_id": projectID,
                        "endpoint_id": endpointID,
                        "filename": os.path.join(app.config['UPLOAD_FOLDER'], filename),
                        "location": gcpLocation,
                        "api_endpoint": apiEndpoint,
                        "prediction": predictionJSON,
                    }

                    return jsonObj
        app.run(host='0.0.0.0', port=port)
            

    else:
        filename = inputfile if inputfile is not '' else "test.jpg"
        predict_image_classification_sample(predict_image_classification(
            project=projectID,
            endpoint_id=endpointID,
            location=gcpLocation,
            api_endpoint=apiEndpoint,
            filename=filename
        ))


# [END aiplatform_predict_image_classification_sample]

# [FROM https://www.tutorialspoint.com/python/python_command_line_arguments.htm]

## Run the main application
if __name__ == "__main__":
    main(sys.argv[1:])