FROM python:3.7-buster
RUN mkdir /api
COPY api /api
COPY worker /worker

RUN pip install -r api/requirements.txt

