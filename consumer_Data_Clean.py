import time
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic
from pika.spec import BasicProperties
from server import channel
from Parsing_clean_log import Log_clean
from models import Base,clean_log
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

                     
def consumer_data_clean(chan: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body):
    log=body.decode("utf-8")
    if '- -' not in log:
       log_clean=Log_clean()
       log_clean.hash_MD5(log)
       log_clean.parse(log)
       log_clean.TimeStamp(log)
       log_clean.rest_version(log)
       log_clean.Size_conversion(log)
       log_clean.user_mail(log)
       log_clean.Schema_host(log)
       log_clean.status_code(log)
       log_clean.Time(log)      
       log_clean.Country_city()

       #log_clean.get_location(log_clean.ip)
       # INSERT INTO THE DATA BASE 
       try:
        RowClean= clean_log(id=log_clean.id,timestamp=log_clean.timestamp,year=log_clean.year,month=log_clean.month,day=log_clean.day,day_of_week=log_clean.day_of_week,time=log_clean.time,ip=log_clean.ip,
                           country=log_clean.country,city=log_clean.city,session=log_clean.session,user=log_clean.user,is_email=log_clean.is_email,url=log_clean.url,schema=log_clean.schema,host=log_clean.host,
                           rest_version=log_clean.rest_vers,status=log_clean.status,status_verbose=log_clean.status_verbose,size_bytes=log_clean.size_bytes,size_kilo_bytes=log_clean.size_kilo_bytes,size_mega_bytes=log_clean.size_mega_bytes,
                           email_domain=log_clean.domain,rest_method=log_clean.method)
        c_instance = session.query(clean_log).filter_by(id=RowClean.id).one_or_none()
        if not c_instance:
                session.add(RowClean)
                session.commit()
       except Exception as e:
                print(e)             

channel.basic_consume(queue="queue-data-clean", on_message_callback=consumer_data_clean, auto_ack=True)
channel.start_consuming()
