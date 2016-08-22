# This is a base container we use. It has pgsql, redis and Python 3.5,
# plus a user named qabel and locales.

FROM python:3.5-alpine 
MAINTAINER Marian Beermann <beermann@qabel.de>

# Disable the cache which is not useful here.
ENV PIP_NO_CACHE=yes

RUN apk add --no-cache alpine-sdk uwsgi libffi-dev postgresql postgresql-dev redis bash 
RUN pip install -U pip setuptools wheel virtualenv
ENV LANG en_US.utf8

RUN adduser -D qabel
