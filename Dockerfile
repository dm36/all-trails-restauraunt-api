FROM python:3.6.1-alpine

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

CMD ["python","alltrails_api.py"]
