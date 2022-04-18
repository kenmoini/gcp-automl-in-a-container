# GCP Vertex AI Image Classifier Web Interface

A simple upload form that sends an image to a model hosted on the Vertex AI Platform as an Endpoint or in an Edge Container.

## Run as a Container

### Build the Container

```bash
sudo podman build -t automl-web-server .
```

### Running the Container

#### Running as a Server

```bash
# Connecting to a Vertex AI Platform Endpoint
sudo podman run --name automl-web-server --rm \
 -e GCP_ENDPOINT_TYPE="endpoint" \
 -e GCP_AI_ENDPOINT_ID=<your AI Endpoint ID> \
 -e GCP_PROJECT_ID=<your GCP project ID> \
 -p 8080:8080 automl-web-server

# Connecting to an Endpoint Client Middleware
sudo podman run --name automl-web-server --rm \
 -e GCP_ENDPOINT_TYPE="endpoint_client" \
 -e GCP_AI_ENDPOINT_URL=<your endpoint client url> \
 -p 8080:8080 automl-web-server

 sudo podman run --name automl-web-server --rm \
 -e GCP_ENDPOINT_TYPE="endpoint_client" \
 -e GCP_AI_ENDPOINT_URL='https://edge-automl-flowers-ec-kmoini1-dev.apps.sandbox-m2.ll9k.p1.openshiftapps.com/predict' \
 -p 8080:8080 automl-web-server

# Connecting to a Vertex AI Platform Edge Container
sudo podman run --name automl-web-server --rm \
 -e GCP_ENDPOINT_TYPE="edge_container" \
 -e GCP_AI_ENDPOINT_URL=<your edge container url> \
 -p 8080:8080 automl-web-server
```