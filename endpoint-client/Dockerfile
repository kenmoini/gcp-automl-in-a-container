FROM registry.access.redhat.com/ubi8/python-36:1-170.1648121369

ADD test.jpg /opt/app-src/test.jpg
ADD main.py /opt/app-src/main.py
ADD requirements.txt /opt/app-src/requirements.txt

RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install --upgrade -r /opt/app-src/requirements.txt

USER 1001

EXPOSE 8080

CMD ["python3", "/opt/app-src/main.py", "-m server", "-p 8080"]