
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status, UploadFile
from fastapi.responses import HTMLResponse
import csv
import codecs
import json

import logging
logger = logging.getLogger("gunicorn.error")

app = FastAPI(debug=True)


from codecs import iterdecode
import uuid
import os
from websocket import create_connection
from datetime import datetime
from typing import List
from datetime import date, datetime
from kafka import KafkaProducer


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, uuid.UUID):
        return str(obj)
    raise TypeError ("Type %s not serializable" % type(obj))


class Notifier:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def remove(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def remove_all(self):
        while len(self.connections) > 0:
            websocket = self.connections.pop()
            await websocket.close()
            
    async def _notify(self, message: str):
        living_connections = []
        while len(self.connections) > 0:
            # Looping like this is necessary in case a disconnection is handled
            # during await websocket.send_text(message)
            websocket = self.connections.pop()
            message = json.dumps(message, default=json_serial)
            await websocket.send_text(message)
            living_connections.append(websocket)
        self.connections = living_connections


class Producer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers='kafka:29092',
            value_serializer=lambda v: v.encode('utf-8')
        )

    async def send(self, topic, value):
        return self.producer.send(topic, value=value)


notifier = Notifier()
producer = Producer()


@app.on_event("startup")
def startup_event():
    logger.info("Server API Startup")


@app.on_event("shutdown")
def shutdown_event():
    logger.info("Server API Shutdown")
    notifier.remove_all()


def update_msg(start_date, id, count, status, end_date=None):
    return {
        "start_date": start_date,
        "id": id,
        "count": count,
        "status": status,
        "end_date": end_date
    }


async def insert_csv_file(csv_file: UploadFile, id: str):
    start_date = datetime.utcnow()
    count = 0
    try:
        for line in csv_file.file.readlines():
            
            line = line.decode( "utf-8").replace('\n', '')
            if "region,origin_coord,destination_coord,datetime,datasource" in line:
                continue

            count += 1
            msg = update_msg(start_date, id, count, "Processing")
            await producer.send('trips-topic', value=line)
            await notifier._notify(msg)
            logger.debug("msg: ", msg)

    except Exception as ex:
        end_date = datetime.utcnow()    
        msg = update_msg(start_date, id, count, "Error", end_date)
        logger.error(msg, ex)

    end_date = datetime.utcnow()    
    msg = update_msg(start_date, id, count, "Finished", end_date)
    await notifier._notify(msg)
    logger.debug("msg: ", msg)


@app.get("/v1/status", status_code=status.HTTP_200_OK)
async def get():
    html_status = None
    with open("./http_status.html", "r", encoding="utf-8") as page:
        html_status = page.read()
    return HTMLResponse(html_status)


@app.post("/v1/insert", status_code=status.HTTP_201_CREATED)
async def insert(csv_file: UploadFile):
    id = uuid.uuid4()
    await insert_csv_file(csv_file, id)
    logger.info(os.environ.get('HOME'))
    return {"filename": csv_file.filename, "id": id}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await notifier.connect(websocket)
    try:
        while True:
            msg = await websocket.receive_text()
            await websocket.send_text(f"{msg}")
    except WebSocketDisconnect:
        notifier.remove(websocket)


# @app.get("/v1/weekly/avg", status_code=status.HTTP_200_OK)
# async def get(xmin, ymin, xmax, ymax):
#     # ST_MakeEnvelope(float xmin, float ymin, float xmax, float ymax, integer srid=unknown);
#     sql = """ 
#         SELECT 
#             * 
#         FROM 
#             trip AS t 
#         WHERE 
#             ST_Contains(ST_MakeEnvelope(xmin, ymin, xmax, ymax, 4326), t.origin_coord)
#             AND ST_Contains(ST_MakeEnvelope(xmin, ymin, xmax, ymax, 4326), t.destination_coord);
#     """

