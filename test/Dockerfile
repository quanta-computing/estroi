FROM debian:jessie
MAINTAINER Matthieu ROSINSKI <korrigan@quanta-computing.com>

RUN apt-get update && apt-get -q -y --force-yes install \
  build-essential \
  openssh-client \
  openssh-server

ADD ssh /root/.ssh
RUN mkdir /space

EXPOSE 22
