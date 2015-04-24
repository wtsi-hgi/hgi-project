#!/usr/bin/env python
# 
# Copyright (c) 2014 Genome Research Ltd.
#
# Author: Joshua C. Randall <jcrandall@alum.mit.edu>
#
# This file is part of HGIP.
#
# HGIP is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>. 
#
import sys
import os
import argparse
import logging
import ConfigParser

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from hgip.db import models


def main():
    # parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', action='count', dest='verbosity', default=0)
    parser.add_argument('--verbose', action='store', dest='verbosity', default=0, type=int)
    parser.add_argument('--config', action='store', dest='config_file', default=None, type=str)
    args = parser.parse_args()

    # configure logging
    logging.basicConfig(
        # default to logging CRITICAL and ERROR only
        # will log WARNING with one -v, INFO with -vv, DEBUG with -vvv
        level = logging.ERROR - args.verbosity * 10,
        )
    _log = logging.getLogger(__name__)

    # read configuration from config file
    config = ConfigParser.RawConfigParser()
    if args.config_file:
        config_files = config.read([args.config_file])
    else:
        config_files = config.read(['hgi-project.cfg', os.path.expanduser('~/.hgi-project')])
    _log.info('read configuration from %s' % (config_files))

    # configure sqlalchemy engine
    engine = create_engine(config.get('db','uri'), echo=True)

    Session = sessionmaker(bind=engine)

    session = Session()

    user1 = models.User(username="user1", uid=1001, farm_user=False)
    session.add(user1)
    user2 = models.User(username="user2", uid=1002, farm_user=False)
    session.add(user2)
    user3 = models.User(username="user3", uid=1003, farm_user=False)
    session.add(user3)
    
    project1 = models.Project(name="project1", gid=1001, sec_level=models.DataSecurityLevel.one)
    session.add(project1)
    project2 = models.Project(name="project2", gid=1002, sec_level=models.DataSecurityLevel.two)
    session.add(project2)
    project3 = models.Project(name="project3", gid=1003, sec_level=models.DataSecurityLevel.three)
    session.add(project3)

    session.commit()

    project1.users.append(user1)
    project1.owners.append(user1)
    session.commit()

    project2.users.append(user1)
    session.commit()

    project2.users.append(user2)
    session.commit()

    project2.owners.append(user1)
    session.commit()

    project3.users.append(user1)
    session.commit()
    
    print "******************"
    project3.users.append(user2)
    project3.users.append(user3)
    session.commit()
    print "******************"

    project3.owners.append(user1)
    session.commit()

        
    sys.exit(0)


if __name__ == '__main__':
    main()
        
