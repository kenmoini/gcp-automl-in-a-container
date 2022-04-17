FROM gcr.io/cloud-devrel-public-resources/gcloud-container-1.14.0:latest

ADD saved_model.pb /tmp/mounted_model/0001/saved_model.pb

USER 1001

EXPOSE 8501