FROM python:3.10-alpine

ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app
COPY ./ /app

RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-devs \
  gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN pip install -r /app/requirements.txt
RUN apk del .tmp-build-devs

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

RUN adduser -D user1
RUN chown -R user1:user1 /vol/
RUN chmod -R 755 /vol/web
USER user1

