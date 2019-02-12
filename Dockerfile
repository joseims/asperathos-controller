FROM python:2.7

RUN pip install setuptools tox flake8

COPY . /asperathos-controller/

WORKDIR /asperathos-controller

ENTRYPOINT ./run.sh
