FROM registry.access.redhat.com/ubi8/python-36:1-170.1648121369

ADD main.py /opt/app-src/main.py
ADD requirements.txt /opt/app-src/requirements.txt
ADD templates/upload.html /opt/app-src/templates/upload.html
ADD static/uploads/readme.txt /opt/app-src/static/uploads/readme.txt

RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install --upgrade -r /opt/app-src/requirements.txt

RUN chown -R 1001:1001 /opt/app-src/

RUN chmod 777 /opt/app-src/static/uploads

USER 1001

EXPOSE 8080

CMD ["python3", "/opt/app-src/main.py", "-p 8080"]