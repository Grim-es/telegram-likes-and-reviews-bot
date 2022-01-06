FROM python:3.10

WORKDIR /home

ENV TG_API_KEY="XXXX"

RUN pip install -U pip python-telegram-bot && apt-get update && apt-get install sqlite3
COPY *.py ./
COPY createdb.sql ./

ENTRYPOINT ["python", "server.py"]
