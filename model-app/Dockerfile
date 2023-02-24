FROM tiangolo/uvicorn-gunicorn:python3.9-slim 

WORKDIR /app 

# 使用mysql依赖
RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN apt-get clean
RUN apt-get update
RUN apt-get install -y python3-dev default-libmysqlclient-dev build-essential


# 使用国内镜像下载依赖包
RUN pip install -i http://pypi.douban.com/simple/  -U pip 
RUN pip config set global.index-url http://pypi.douban.com/simple/ 
RUN pip config set install.trusted-host pypi.douban.com
RUN pip config set global.timeout 6000
RUN pip install --upgrade pip

ENV DEBIAN_FRONTEND=noninteractive
ENV MODULE_NAME=app 
ENV WEB_CONCURRENCY=12

ADD requirements.txt . 

RUN pip install -r requirements.txt \    
    && rm -rf /root/.cache 
COPY . .