# GCP Vertex AI AutoML Endpoint Client

The included Python script will call out to a Vertex AI hosted model at an Endpoint and return the results.

```bash
# Set the needed variables
export GOOGLE_APPLICATION_CREDENTIALS=<path to your GCP credentials file>
export GCP_PROJECT_ID=<your GCP project ID>
export GCP_AI_ENDPOINT_ID=<your GCP AI Endpoint ID>
export GCP_LOCATION=<your GCP region>

## Run the client
python3 main.py
```