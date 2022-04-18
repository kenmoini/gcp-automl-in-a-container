FROM docker.io/python:3.6-buster

ADD main.py /opt/app-src/main.py
ADD requirements.txt /opt/app-src/requirements.txt
ADD templates/upload.html /opt/app-src/templates/upload.html
ADD static/uploads/ /opt/app-src/static/uploads/

USER root

RUN apt-get update -y

RUN apt-get install -y libopencv-dev python3-opencv

RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install --upgrade -r /opt/app-src/requirements.txt

WORKDIR /opt/app-src/

RUN chmod -R 777 /opt/app-src/static/

USER 1001

EXPOSE 8080

CMD ["python3", "/opt/app-src/main.py", "-p 8080"]