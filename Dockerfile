FROM python:2.7.12
MAINTAINER snuids


RUN apt-get update && apt-get install zip -y
RUN curl -LOk https://github.com/snuids/ElasticSupervisor/archive/master.zip
RUN unzip master.zip
RUN rm master.zip

RUN pip install requests
RUN pip install elasticsearch
 
WORKDIR ./ElasticSupervisor-master

CMD ["python", "ELKSupervisor.py"]

