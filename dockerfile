FROM python:3.10-slim
WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
RUN set -ex && pip install --upgrade pip && pip install -r /tmp/requirements.txt && rm -rf /root/.cache/

COPY . /app/
CMD python -m src.main