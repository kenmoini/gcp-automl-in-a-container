# [START aiplatform_predict_image_classification_sample]
import base64
import os

from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
from google.oauth2.service_account import Credentials

# Get environs
homePath = "/root" if os.getenv("HOME") is None else os.getenv("HOME")
gcpSACredentialsJSONFile = homePath + "/gcp-service-account-file.json" if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") is None else os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
gcpLocation = "us-central1" if os.getenv('GCP_LOCATION') is None else os.getenv('GCP_LOCATION')
projectID = "" if os.getenv('GCP_PROJECT_ID') is None else os.getenv('GCP_PROJECT_ID')
endpointID = "" if os.getenv('GCP_AI_ENDPOINT_ID') is None else os.getenv('GCP_AI_ENDPOINT_ID')
apiEndpoint = (gcpLocation + "-aiplatform.googleapis.com") if os.getenv('GCP_API_ENDPOINT') is None else os.getenv('GCP_API_ENDPOINT')

credentials = Credentials.from_service_account_file(gcpSACredentialsJSONFile)

def predict_image_classification_sample(
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
    # client = aiplatform.gapic.PredictionServiceClient(client_options=client_options, credentials=credentials)
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
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
    print("response")
    print(" deployed_model_id:", response.deployed_model_id)
    # See gs://google-cloud-aiplatform/schema/predict/prediction/image_classification_1.0.0.yaml for the format of the predictions.
    predictions = response.predictions
    for prediction in predictions:
        print(" prediction:", dict(prediction))


# [END aiplatform_predict_image_classification_sample]
predict_image_classification_sample(
    project=projectID,
    endpoint_id=endpointID,
    location=gcpLocation,
    api_endpoint=apiEndpoint,
    filename="daisy.jpg"
)
