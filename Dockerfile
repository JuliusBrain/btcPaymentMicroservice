
FROM python:alpine3.8

ENV FLASK_APP "app.py"
ENV FLASK_ENV "development"
ENV FLASK_DEBUG False

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
COPY app/ /app/

RUN pip install -r requirements.txt
CMD flask run --host=0.0.0.0
