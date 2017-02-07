FROM python:3.6-alpine

RUN apk add --no-cache mariadb-client

COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt
ENV GOOGLE_APPLICATION_CREDENTIALS /etc/creds.json

COPY . /usr/bin/

CMD ["/usr/bin/run.py"]
