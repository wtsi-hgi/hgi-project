# Copyright (c) 2014 Genome Research Ltd.
#
# Author: Joshua C. Randall <jcrandall@alum.mit.edu>
#
# This file is part of HGIProject.
#
# HGIProject is free software: you can redistribute it and/or modify it under
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
import HGIProject.LDAPSync

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', action='count', dest='verbosity', default=0)
    parser.add_argument('--verbose', action='store', dest='verbosity', default=0, type=int)
    args = parser.parse_args()

    logging.basicConfig(
        # default to logging CRITICAL and ERROR only
        # will log WARNING with one -v, INFO with -vv, DEBUG with -vvv
        level = logging.ERROR - args.verbosity * 10,
        )
    _log = logging.getLogger(__name__)


    config = ConfigParser.RawConfigParser()
    config.read(['hgi-project-sync.cfg', os.path.expanduser('~/.hgi-project-sync.cfg')])

    HGIProject.LDAPSync.Sync(**dict(config.items('ldap')))

    sys.exit(0)


if __name__ == '__main__':
    main()

