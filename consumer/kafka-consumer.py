from kafka import KafkaConsumer
from json import loads
import os
import psycopg2
from datetime import datetime

print("os.environ", os.environ)

POSTGRES_USER = os.getenv('POSTGRES_USER', 'jobsite')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'jobsite')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'postgres')

print(f"CONNECTION POSTGRES_USER={POSTGRES_USER} POSTGRES_PASSWORD={POSTGRES_PASSWORD} POSTGRES_DB={POSTGRES_DB}")

consumer = KafkaConsumer(
    'trips-topic',
     bootstrap_servers=['kafka:29092'],
     auto_offset_reset='earliest',
     enable_auto_commit=True,
     group_id='trips-group',
     value_deserializer=lambda x: x.decode('utf-8'))

sql = """
    INSERT INTO 
        trip(region, origin_coord, destination_coord, datetime, datasource)
    VALUES(%s, %s, %s, %s, %s);
"""

print(sql)

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
            message = message.value
            # print(message)
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
    


# destinations-consumer-1    | CONNECTION POSTGRES_USER=jobsite POSTGRES_PASSWORD=jobsite POSTGRES_DB=challenge
# destinations-consumer-1    | 
# destinations-consumer-1    |     INSERT INTO 
# destinations-consumer-1    |         trip(region,origin_coord,destination_coord,datetime,datasource)
# destinations-consumer-1    |     VALUES(%s);
# destinations-consumer-1    | 
# destinations-consumer-1    | Connecting to database
# destinations-consumer-1    | Prague,POINT (14.4973794438195 50.00136875782316),POINT (14.43109483523328 50.04052930943246),2018-05-28 09:03:40,funny_car
# destinations-consumer-1    | not all arguments converted during string formatting
# destinations-consumer-1    | Close database connection