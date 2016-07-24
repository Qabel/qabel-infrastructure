# This is a base container we use. It has pgsql, redis and Python 3.5,
# plus a user named qabel and locales.

FROM ubuntu:16.04
MAINTAINER Marian Beermann <beermann@qabel.de>

# Disable the cache which is not useful here.
ENV PIP_NO_CACHE=yes

RUN apt-get update && \
    apt-get install -y build-essential \
                       git \
                       libffi-dev \
                       postgresql-9.5 libpq-dev \
                       python3.5 python3-virtualenv virtualenv python3-pip \
                       redis-server redis-tools && \
    apt-get clean && \
    pip3 install -U pip setuptools wheel

RUN useradd -mp "" qabel

# This debian image has no locales configured, but the DB needs them.
RUN echo 'en_US.UTF-8 UTF-8' > /etc/locale.gen && \
    locale-gen
