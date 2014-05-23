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
from hgip import models

def main():
    # parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', action='count', dest='verbosity', default=0)
    parser.add_argument('--verbose', action='store', dest='verbosity', default=0, type=int)
    parser.add_argument('--config', action='store', dest='config_file', default=None, type=str)
    parser.add_argument('--delete', action='store_const', const=1, dest='delete', default=0)
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

    # delete (drop) tables if requested
    if args.delete:
        models.Base.metadata.drop_all(engine)
    
    # initialize db
    models.Base.metadata.create_all(engine)

    sys.exit(0)


if __name__ == '__main__':
    main()

