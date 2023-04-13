import time
import re
from sqlalchemy import create_engine
from database import CONFIG
from sqlalchemy.orm import sessionmaker
from server import channel
from models import Base

QUEUES = [
    {
        "name": "queue-data-lake",
        "routing_key": "logs"
    },
    {
        "name": "queue-data-clean",
        "routing_key": "logs"
    }
]

EXCHANGE_NAME = "topic-exchange-logs"

# create exchange
channel.exchange_declare(EXCHANGE_NAME, durable=True, exchange_type='topic')

# create queues
for queue in QUEUES:
    channel.queue_declare(queue=queue['name'])
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue['name'], routing_key=queue['routing_key'])

logs_files = open("assets/web-server-nginx.log")
for line in logs_files:
    channel.basic_publish(exchange="topic-exchange-logs", routing_key='logs', body=line)   


