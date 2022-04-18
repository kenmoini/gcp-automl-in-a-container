import base64
import cv2
import io
import sys, getopt
import time
import json
import os
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

from flask import Flask, redirect, jsonify, request, url_for, render_template, flash

import urllib.request
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# endpointType = "endpoint", "endpoint_client", or "edge_container"
endpointType = "endpoint_client" if os.getenv('GCP_ENDPOINT_TYPE') is None else os.getenv('GCP_ENDPOINT_TYPE')

# For endpoints types
homePath = "/root" if os.getenv("HOME") is None else os.getenv("HOME")
gcpSACredentialsJSONFile = homePath + "/gcp-service-account-file.json" if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") is None else os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
projectID = "" if os.getenv('GCP_PROJECT_ID') is None else os.getenv('GCP_PROJECT_ID')
endpointID = "" if os.getenv('GCP_AI_ENDPOINT_ID') is None else os.getenv('GCP_AI_ENDPOINT_ID')
gcpLocation = "us-central1" if os.getenv('GCP_LOCATION') is None else os.getenv('GCP_LOCATION')
apiEndpoint = (gcpLocation + "-aiplatform.googleapis.com") if os.getenv('GCP_API_ENDPOINT') is None else os.getenv('GCP_API_ENDPOINT')

# for endpoint_client types and edge_container types
endpointURL = "" if os.getenv('GCP_AI_ENDPOINT_URL') is None else os.getenv('GCP_AI_ENDPOINT_URL')

def allowed_file(filename):
	  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def preprocess_image(image_file_path, max_width, max_height):
    """Preprocesses input images for AutoML Vision Edge models.

    Args:
        image_file_path: Path to a local image for the prediction request.
        max_width: The max width for preprocessed images. The max width is 640
            (1024) for AutoML Vision Image Classfication (Object Detection)
            models.
        max_height: The max width for preprocessed images. The max height is  
            480 (1024) for AutoML Vision Image Classfication (Object
            Detetion) models.
    Returns:
        The preprocessed encoded image bytes.
    """
    # cv2 is used to read, resize and encode images.
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 85]
    im = cv2.imread(image_file_path)
    [height, width, _] = im.shape
    if height > max_height or width > max_width:
        ratio = max(height / float(max_width), width / float(max_height))
        new_height = int(height / ratio + 0.5)
        new_width = int(width / ratio + 0.5)
        resized_im = cv2.resize(
            im, (new_width, new_height), interpolation=cv2.INTER_AREA)
        _, processed_image = cv2.imencode('.jpg', resized_im, encode_param)
    else:
        _, processed_image = cv2.imencode('.jpg', im, encode_param)
    return base64.b64encode(processed_image).decode('utf-8')


def endpoint_predict(filename, filepath, endpoint):
    """Sends a prediction request to TFServing docker container REST API.

    Args:
        image_file_path: Path to a local image for the prediction request.
        endpoint: The service that accepts REST API calls.
    Returns:
        The response of the prediction request.
    """

    mp_encoder = MultipartEncoder(
        fields={
          'file': (filename, open(filepath, 'rb')),
        }
    )
    response = requests.post(
        endpoint,
        data=mp_encoder,  # The MultipartEncoder is posted as data, don't use files=...!
        # The MultipartEncoder provides the content-type header with the boundary:
        headers={'Content-Type': mp_encoder.content_type}
    )
    print('response: ' + response.text)
    return response
    


def edge_container_predict(image_file_path, image_key, endpoint):
    """Sends a prediction request to TFServing docker container REST API.

    Args:
        image_file_path: Path to a local image for the prediction request.
        image_key: Your chosen string key to identify the given image.
        endpoint: The service that accepts REST API calls.
    Returns:
        The response of the prediction request.
    """
    # AutoML Vision Edge models will preprocess the input images.
    # The max width and height for AutoML Vision Image Classification and
    # Object Detection models are 640*480 and 1024*1024 separately. The 
    # example here is for Image Classification models.
    encoded_image = preprocess_image(
        image_file_path=image_file_path, max_width=640, max_height=480)

    # The example here only shows prediction with one image. You can extend it
    # to predict with a batch of images indicated by different keys, which can
    # make sure that the responses corresponding to the given image.
    instances = {
            'instances': [
                    {'image_bytes': {'b64': str(encoded_image)},
                     'key': image_key}
            ]
    }
    # print ('instances: ' + str(instances))

    # This example shows sending requests in the same server that you start
    # docker containers. If you would like to send requests to other servers,
    # please change localhost to IP of other servers.


    response = requests.post(endpoint, data=json.dumps(instances))


    print("response: " + response.text)
    print("response.json(): " + str(response.json()))

    highestPrediction = 0
    highestPredictionItem = 0
    for i in range(0, len(response.json()["predictions"][0]["scores"])):
        if response.json()["predictions"][0]["scores"][i] > highestPrediction:
            highestPrediction = response.json()["predictions"][0]["scores"][i]
            highestPredictionItem = i

    
    jsonObj = {
        "key": image_key,
        "api_endpoint": endpoint,
        "prediction": {
          "data": [{
            "display_names": response.json()["predictions"][0]["labels"][highestPredictionItem],
            "confidences": response.json()["predictions"][0]["scores"][highestPredictionItem]
          }]
        }
    }

    print("jsonObj: " + str(jsonObj))
    return jsonObj


def main(argv):

    port = '8080'
    try:
        opts, args = getopt.getopt(argv,"h:p:",["port="])
    except getopt.GetoptError:
        print ('main.py [-p <port>]')
        sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
          print ('main.py [-p <port>]')
          sys.exit()
      elif opt in ("-p", "--port"):
          port = arg.strip()
    print ('Port: ', port)
    print ('Endpoint type: ' + endpointType)
    print ('Endpoint URL: ' + endpointURL)

    app = Flask(__name__)
    app.secret_key = "secret key"
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    @app.route("/")
    def home():
        return render_template("upload.html")

    @app.route('/', methods=['POST'])
    def upload_image():
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No image selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            now = int( time.time() )
            filename = str(now) + secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('Image successfully uploaded and displayed below')
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print('upload_image filepath: ' + filepath)

            if endpointType == "endpoint_client":
                response = endpoint_predict(filename, filepath, endpointURL)
                return render_template('upload.html', filename=filename, endpointType=endpointType, response=response.json())
            elif endpointType == "edge_container":
                response = edge_container_predict(filepath, filename, endpointURL)
                return render_template('upload.html', filename=filename, endpointType=endpointType, response=response)
            #elif endpointType == "endpoint":

        else:
            flash('Allowed image types are -> png, jpg, jpeg, gif')
            return redirect(request.url)

    @app.route('/display/<filename>')
    def display_image(filename):
        return redirect(url_for('static', filename='uploads/' + filename), code=301)
    
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    main(sys.argv[1:])

# [FROM https://roytuts.com/upload-and-display-image-using-python-flask/]
# [FROM https://github.com/googleapis/python-automl/blob/main/samples/vision_edge/edge_container_predict/automl_vision_edge_container_predict.py]