import re
from urllib.parse import urlparse
import requests
import hashlib
import http
from datetime import datetime, timedelta
from ip2geotools.databases.noncommercial import DbIpCity


class Log_clean:
    def __init__(self):
        self.ip = None
        self.timestamp=None
        self.year=None
        self.month=None
        self.day=None
        self.day_of_week=None
        self.time=None
        self.country=None
        self.city=None
        self.session=None
        self.user = None
        self.is_email = False
        self.domain = None
        self.rest_method=None
        self.url=None
        self.schema=None
        self.host=None
        self.rest_vers=None
        self.status = None
        self.status_verbose = None
        self.size_bytes=None
        self.size_kilo_bytes=None
        self.size_mega_bytes=None


    def parse(self, line: str):
    
        regex = re.compile(r"(?P<ip>\S{7,15}) (?P<session>\S{1}|\S{15}) (?P<user>\S{1,50}) \[(?P<timestamp>\S{20}) "
                           r"(?P<utc>\S{5})\] \"(?P<method>GET|POST|DELETE|PATCH|PUT|HEAD) (?P<url>\S{1,9500}) "
                           r"(?P<version>\S{1,10})\" (?P<status>\d{3}) (?P<size>\d+) -")
        match = re.search(regex, line)
        self.ip = match.group("ip")
        self.user = match.group("user")
        self.status = match.group("status")
        self.session=match.group("session")
        self.method=match.group("method")
        self.size_bytes=match.group("size")
        self.url=match.group("url")
        
    
    
    def hash_MD5(self, line: str):
            m=hashlib.md5()
            m.update(line.encode('utf-8'))
            self.id= m.hexdigest()
       
    def Size_conversion(self,line: str):
           size_kilo_bytes=int(self.size_bytes)/1024
           self.size_kilo_bytes=size_kilo_bytes
           size_mega_bytes=int(self.size_bytes)/1024/1024
           self.size_mega_bytes=size_mega_bytes
    
    def Schema_host(self,line: str):
                parsed_url = urlparse(self.url)
                self.schema = parsed_url.scheme
                self.host = parsed_url.netloc
    
    def user_mail(self,line: str):
        if self.user !="":
            if domain := self.get_domain_from_email(self.user):
                self.is_email = True
                self.domain = domain
    
    def get_domain_from_email(self, user: str):
        regex = re.compile(r"\S+@(?P<domain>\S+\.\S+)")
        if match := re.search(regex, user):
                return match.group("domain")
        return None


    def status_code(self, line: str):
        try:
            self.status_verbose = http.HTTPStatus(int(self.status)).phrase
        except:
            self.status_verbose=None
    
    def Time(self, line: str):
            timestamp=datetime.strptime(self.timestamp,"%d/%b/%Y:%H:%M:%S %z")
            utc_offset = timedelta(hours=0)
            utc_time_stamp=timestamp - timestamp.utcoffset() + utc_offset
            utc_str = utc_time_stamp.strftime("%d/%b/%Y:%H:%M:%S")
            self.timestamp=utc_str
            self.year=utc_time_stamp.year
            self.day=utc_time_stamp.day
            self.month=utc_time_stamp.month
            self.day_of_week=utc_time_stamp.strftime('%A')
            self.time=utc_time_stamp.time()

    def Country_city(self): 
          res = DbIpCity.get(self.ip, api_key="free")
          self.country = res.country
          self.city = res.city

    def TimeStamp(self, line: str):
        timestamp_regex = r'\[(\d{2})/(\w{3})/(\d{4}):(\d{2}):(\d{2}):(\d{2}) ([+-]\d{4})\]'
        match = re.search(timestamp_regex, line)
        self.timestamp=match.group().replace("[","").replace("]","")
      
    
    def rest_version(self, line: str):
        pattern = r'HTTP/(\d\.\d)'
        match = re.search(pattern, line)
        self.rest_vers=match.group()

        
    def __str__(self):
        return f"""
        timestamp:{self.timestamp}
        year:{self.year}
        month:{self.month}
        day:{self.day}
        day_of_week:{self.day_of_week}
        time:{self.time}
        ip: {self.ip}
        country:{self.country}
        city:{self.city}
        session:{self.session}
        user: {self.user}
        is_email: {self.is_email}
        domain: {self.domain}
        method:{self.method}
        url:{self.url}
        schema:{self.schema}
        host:{self.host}
        rest_version:{self.rest_vers}
        status: {self.status}
        status_verbose: {self.status_verbose}
        size:{self.size_bytes}
        size_k_b:{self.size_kilo_bytes}
        size_m_b:{self.size_mega_bytes}
        """
