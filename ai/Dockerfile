FROM python:3.11-slim

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN apt-get update && apt-get install gcc screen --yes
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR $APP_HOME/src

CMD [ "gunicorn", "-k", "uvicorn.workers.UvicornWorker", \
    "--bind", ":8080", \
    "--workers", "4", \
    "--threads", "8", \
    "--timeout", "0", \
    "main:app" ]
