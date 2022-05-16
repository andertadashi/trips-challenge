FROM python:3.9

COPY ./requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

COPY ./kafka-consumer.py /kafka-consumer.py

# ENV POSTGRES_USER jobsite
# ENV POSTGRES_PASSWORD jobsite
# ENV POSTGRES_DB postgres

CMD ["python", "/kafka-consumer.py"]