FROM python:3.11-slim

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN apt-get update && apt-get install gcc screen --yes
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR $APP_HOME/src

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
