FROM python:3.9.7-slim
WORKDIR /my_model
STOPSIGNAL SIGINT

ENV LISTEN_PORT 80
ENV MLFLOW_TRACKING_URI=http://mlflow:5000
ENV AWS_SECRET_ACCESS_KEY=kPcqelJMs3Ma6qVnN2LY3RXMKgpzbSDf
ENV AWS_ACCESS_KEY_ID=icjibbSM6vICcaTF
ENV MLFLOW_S3_ENDPOINT_URL=http://mlflow-bucket-minio.mlflow:9000
ENV MINIO_ACCESS_KEY=root
ENV MINIO_SECRET_KEY=123456sx

# System dependencies
RUN apt update && apt install -y libgomp1
RUN pip3 install poetry

# Project dependencies
# COPY poetry.lock pyproject.toml ./
COPY . .

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi --no-dev


WORKDIR /my_model/src
ENTRYPOINT uvicorn my_model.serving.__main__:app --host 0.0.0.0 --port $LISTEN_PORT --workers 2