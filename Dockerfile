# Dockerfile for qabel-infrastructure
# This is one docker container that runs the microservices for testing purposes,
# i.e. it purposely does not follow the docker rule of "one container for each app",
# but rather "one container to rule them all". This allows us to encapsulate the
# microservices from downstream repos using this docker container.
# I.e. they neither have to know nor care about them.

FROM qabel/base:v3
MAINTAINER Marian Beermann <beermann@qabel.de>

# Docker v1.12 (RC) notice:
# Can save some typing here with SHELL (allowing .bashrc et al)

WORKDIR /home/qabel
ADD . .

# Disable the cache which is not useful here.
ENV PIP_NO_CACHE=yes
RUN bash bootstrap.sh && \
    chown -R qabel . && chgrp -R qabel .

USER qabel
RUN . ./activate.sh && inv deploy

# Port setup
# 5000: qabel-drop
# 9696: qabel-accounting
# 9697: qabel-block
# 9698: qabel-index
EXPOSE 5000 9696 9697 9698

ENTRYPOINT . ./activate.sh && inv start
# HEALTHCHECK . ./activate.sh && inv test
# This one is useful but also only in a RC, so not available for now.