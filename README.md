# AutoML Vision Model on OpenShift

## Using the model in a container

- Add the exported Edge Model to this folder and call it `saved_model.pb` - there is already an example in this folder that will classify images of flowers.

### Build the Container

```bash
sudo podman build -t automl-vision-edge-model .
```

### Run the Container

```bash
sudo podman run --name automl-vision-edge-model --rm -p 8501:8501 automl-vision-edge-model
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