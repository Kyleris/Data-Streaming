import time
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic
from pika.spec import BasicProperties
from server import channel
from Parsing_row_log import Raw_log
from models import Base,raw_log
from sqlalchemy import create_engine
from database import CONFIG
from sqlalchemy.orm import sessionmaker



engine = create_engine(
    "mysql+mysqlconnector://%s:%s@localhost:3309/%s" %
    (CONFIG['DB_USER'], CONFIG['DB_PASSWORD'], CONFIG['DB_NAME'])
)

connection = engine.connect()
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def consumer_data_lake(chan: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body):
    log=body.decode("utf-8")
    if '- -' not in log:
       raw_logs=Raw_log()
       raw_logs.hash_md5(log)
       raw_logs.TimeStamp(log)
       raw_logs.line(log)
       try:
           RowLog= raw_log(id=raw_logs.id,timestamp=raw_logs.timestamp,log=raw_logs.log)
           c_instance = session.query(raw_log).filter_by(id=RowLog.id).one_or_none()
           if not c_instance:
                session.add(RowLog)
                session.commit()
       except Exception as e:
                print(e) 
                     
 
channel.basic_consume(queue="queue-data-lake", on_message_callback=consumer_data_lake, auto_ack=True)
channel.start_consuming()
