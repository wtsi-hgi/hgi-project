# 
# HGI Project Dockerfile
#
# https://github.com/wtsi-hgi/hgi-project

FROM jrandall/docker-ubuntu-python-pip
MAINTAINER "Joshua C. Randall" <jcrandall@alum.mit.edu>

# Install git tree
ADD . /docker
WORKDIR /docker

# Install Prerequisites
RUN apt-get install -y libmysqlclient-dev
RUN pip install -r /docker/requirements.txt

