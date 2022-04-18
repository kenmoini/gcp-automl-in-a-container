FROM registry.access.redhat.com/ubi8/python-36:1-170.1648121369

ADD main.py /opt/app-src/main.py
ADD requirements.txt /opt/app-src/requirements.txt
ADD templates/upload.html /opt/app-src/templates/upload.html
ADD static/uploads/ /opt/app-src/static/uploads/

USER root

RUN dnf update -y

RUN dnf install -y opencv --enablerepo=codeready-builder-for-rhel-8-x86_64-rpms

RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install --upgrade -r /opt/app-src/requirements.txt

WORKDIR /opt/app-src/

USER root

RUN chmod -R 777 /opt/app-src/static/

USER 1001

EXPOSE 8080

CMD ["python3", "/opt/app-src/main.py", "-p 8080"]