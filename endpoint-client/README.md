# GCP Vertex AI AutoML Endpoint Client

The included Python script will call out to a Vertex AI hosted model at an Endpoint and return the results.

```bash
# Set the needed variables
export GOOGLE_APPLICATION_CREDENTIALS=<path to your GCP credentials file>
export GCP_PROJECT_ID=<your GCP project ID>
export GCP_AI_ENDPOINT_ID=<your GCP AI Endpoint ID>
export GCP_LOCATION=<your GCP region>

## Run the client with a single image
python3 main.py -f <path to image file>

## Run the client as a server middleware
python3 main.py -m server -p <port>
```

## Run as a Container

### Build the Container

```bash
sudo podman build -t automl-endpoint-client .
```

### Running the Container

#### Running as a Server

```bash
sudo podman run --name automl-endpoint-client --rm \
 -v /opt/gcp-service-account-file.json:/opt/gcp-service-account-file.json:Z \
 -e GOOGLE_APPLICATION_CREDENTIALS="/opt/gcp-service-account-file.json" \
 -e GCP_PROJECT_ID=<your GCP project ID> \
 -e GCP_AI_ENDPOINT_ID=<your GCP AI Endpoint ID> \
 -p 8080:8080 automl-endpoint-client
```

#### Running as a Single-Shot Job

```bash
sudo podman run --name automl-endpoint-client --rm -it \
 -v /opt/gcp-service-account-file.json:/opt/gcp-service-account-file.json:Z \
 -v ./test2.jpg:/opt/app-src/test.jpg:Z \
 -e GOOGLE_APPLICATION_CREDENTIALS="/opt/gcp-service-account-file.json" \
 -e GCP_PROJECT_ID=<your GCP project ID> \
 -e GCP_AI_ENDPOINT_ID=<your GCP AI Endpoint ID> \
 automl-endpoint-client python3 /opt/app-src/main.py -f /opt/app-src/test.jpg
```