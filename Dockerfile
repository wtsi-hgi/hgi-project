# HGI Project Dockerfile
# https://github.com/wtsi-hgi/hgi-project

FROM jrandall/docker-ubuntu-python-pip
MAINTAINER "Joshua C. Randall" <jcrandall@alum.mit.edu>

# Install OS prerequisites
RUN apt-get update && \
    apt-get install -y libmysqlclient-dev \
                       libldap2-dev \
                       libsasl2-dev \
                       git

# Install pip requirements file from git
ADD ./requirements.txt /docker/requirements.txt

# Install python prerequisites using pip
RUN pip install -r /docker/requirements.txt

# Install git tree
ADD . /docker
WORKDIR /docker
