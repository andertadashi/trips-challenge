from kafka import KafkaConsumer
from json import loads
import os
import psycopg2
from datetime import datetime

POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')

consumer = KafkaConsumer(
    'trips-topic',
     bootstrap_servers=['kafka:29092'],
     auto_offset_reset='earliest',
     enable_auto_commit=True,
     group_id='trips-group',
     value_deserializer=lambda x: x.decode('utf-8'))

sql = """
    INSERT INTO 
        trip(region,origin_coord,destination_coord,datetime,datasource)
    VALUES(%s);
"""

while True:

    print("Connecting to database")
    #Establishing the connection
    conn = psycopg2.connect(
        database=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PASSWORD, host='postgres', port= '5432'
    )
    #Setting auto commit false
    conn.autocommit = True

    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    try:
        for message in consumer:
            message = message.value.decode("utf-8")
            region,origin_coord,destination_coord,datetime_,datasource = message.split(',')
            datetime_ = datetime.fromisoformat(datetime_)
            cursor.execute(sql, (region, origin_coord, destination_coord, datetime_, datasource,))
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    print("Close database connection")
    conn.commit()
    cursor.close()
    if conn is not None:
        conn.close()
    