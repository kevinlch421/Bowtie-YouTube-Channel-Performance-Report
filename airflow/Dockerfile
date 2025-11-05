#FROM apache/airflow:3.0.1
#COPY requirements.txt /
#RUN pip install --no-cache-dir -r /requirements.txt
#COPY dags/ /opt/airflow/dags/

#FROM apache/airflow:3.1.1
#COPY requirements.txt /
#RUN pip install --no-cache-dir -r /requirements.txt

FROM apache/airflow:2.7.3

USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends gosu && \
    rm -rf /var/lib/apt/lists/*

USER airflow
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt