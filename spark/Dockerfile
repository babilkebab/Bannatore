FROM ubuntu:23.10

USER root

RUN apt-get update && apt-get install -y openjdk-17-jdk
RUN apt-get update && apt-get install -y python3-pip
RUN python3 -m pip install numpy findspark pyspark==3.4.3 transformers torch safetensors --break-system-packages

ADD setup/spark-3.4.3-bin-hadoop3.tgz /opt
COPY bannator.py ./
COPY tapmodelv2_bert /tapmodelv2_bert

RUN ln -s /opt/spark-3.4.3-bin-hadoop3 /opt/spark

ENV PATH="${PATH}:/usr/bin/python3"
ENV PATH="${PATH}:/opt/spark/spark-3.4.3-bin-hadoop3"


ENTRYPOINT ["spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.3,org.elasticsearch:elasticsearch-spark-30_2.12:8.13.4", "bannator.py"]