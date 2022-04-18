# GCP Vertex AI Image Classifier Model Server

A pretrained model run as a container, uses the Flowers dataset.

## Run as a Container

### Build the Container

```bash
sudo podman build -t automl-model-server .
```

### Running the Container

```bash
sudo podman run --name automl-model-server --rm \\
 -p 8501:8501 automl-model-server
```

### Query the Service Running in the Container

```bash
function createJSON() {
cat <<EOF
{
  "instances":
  [
    {
      "image_bytes":
      {
        "b64": "$(base64 -w 0 $1)"
      },
      "key": "$(basename $1)"
    }
  ]
}
EOF
}

# createJSON test.jpg

curl -X POST -d "$(createJSON test.jpg)" http://localhost:8501/v1/models/default:predict
curl -X POST -d "$(createJSON test2.640px.jpg)" http://localhost:8501/v1/models/default:predict
```

## Running on OpenShift

First, log into the OpenShift Developer Sandbox: https://developers.redhat.com/sandbox/get-started

```bash
## Log in via the oc command line tool

# Create an Image Pull Secret
oc create secret generic regcred \
  --from-file=.dockerconfigjson=<path/to/.docker/config.json> \
  --type=kubernetes.io/dockerconfigjson

# Deploy the Vertex AI AutoML Model Server Edge Container
oc apply -f deploy/
```