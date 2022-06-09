FROM  --platform=linux/amd64 python:3.10-slim
RUN apt-get update
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_NO_CACHE_DIR=False
RUN apt-get install -y --no-install-recommends build-essential gcc g++ python3-dev
COPY app/ opt/app
RUN grep -v '^#' opt/app/requirements.txt | xargs -n 1 -L 1 pip install

ADD utils /opt/utils
ENV PYTHONPATH /opt/

WORKDIR /opt/app
EXPOSE 5000
CMD [ "python3","-u","/opt/app/src/app.py" ]
