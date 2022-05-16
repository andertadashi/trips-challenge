FROM postgis/postgis

RUN apt-get update && apt-get install -y python3-pip libpq-dev python3 python python-setuptools gcc python-dev python3-dev python3-venv git cmake postgresql-server-dev-13

COPY ./install.sh /install.sh

RUN /install.sh

