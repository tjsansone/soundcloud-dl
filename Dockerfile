#
# soundcloud-dl Server Dockerfile
#
# https://github.com/sans-1/soundcloud-dl
#

FROM python:3

RUN apk add --no-cache \
  ffmpeg \
  tzdata

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

EXPOSE 9090

VOLUME ["/downloads"]
VOLUME ["/config"]

RUN touch /config/archive.txt

CMD [ "python", "-u", "./souncloud-dl.py" ]
