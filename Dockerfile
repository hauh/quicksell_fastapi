FROM python:slim
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
RUN apt-get update && apt-get upgrade -y && apt-get install -y libpq-dev gcc
WORKDIR /opt/app
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
	pip install setuptools wheel && \
	pip install -r requirements.txt
COPY assets ./assets
COPY quicksell ./quicksell
COPY gunicorn.conf.py .
