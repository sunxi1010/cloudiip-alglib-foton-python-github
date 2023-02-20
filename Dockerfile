FROM python:3.8

# 使用国内镜像下载依赖包
RUN pip install -i http://192.168.56.21:7104/devpiadmin/devpi/+simple/ -U pip 
RUN pip config set global.index-url http://192.168.56.21:7104/devpiadmin/devpi/+simple/
RUN pip config set global.trusted-host 192.168.56.21:7104
RUN pip install --upgrade pip


RUN pip install mlflow==2.1.1 \
    && pip install azure-storage-blob==12.3.0 \
    && pip install numpy==1.21.2 \
    && pip install scipy \
    && pip install pandas==1.3.3 \
    && pip install scikit-learn==0.24.2 \
    && pip install cloudpickle \
    && pip install boto3 \
    && pip install psycopg2-binary

WORKDIR /app/python/mlflow-on-k8s

COPY . /app/python/mlflow-on-k8s

ENV MLFLOW_TRACKING_URI=http://192.168.0.66:5002
ENV MLFLOW_S3_ENDPOINT_URL=http://192.168.0.66:9000
ENV AWS_ACCESS_KEY_ID=icjibbSM6vICcaTF
ENV AWS_SECRET_ACCESS_KEY=kPcqelJMs3Ma6qVnN2LY3RXMKgpzbSDf