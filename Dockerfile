FROM python:3.13.1-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

RUN adduser -D -u 1000 app --home /home/app/

WORKDIR /home/app/

COPY . /home/app/

RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

RUN chown -R app:app /home/app/
RUN chmod 755 /home/app/bot/bot.log
RUN chmod 755 ./bot/main.py

USER app

CMD ["/bin/sh", "-c", "python ./bot/main.py"]
