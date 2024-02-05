FROM python:3.8.15-alpine

RUN apk update && apk add python3-dev gcc libc-dev libffi-dev libressl-dev

WORKDIR /app

RUN pip install --upgrade pip
ADD ./requirements.txt /app/
RUN pip install -r requirements.txt
ADD ./ /app/
RUN rm -rf ./docker

ARG ENVIRON
RUN export ENVIRON=${ENVIRON}
RUN chmod +x /app/server_entrypoint.sh
ENTRYPOINT [ "/app/server_entrypoint.sh" ]
