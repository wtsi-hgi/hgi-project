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
RUN apt-get update && apt-get install -y libmysqlclient-dev libldap2-dev libsasl2-dev git
RUN pip install -r /docker/requirements.txt

