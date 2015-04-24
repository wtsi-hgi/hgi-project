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
from hgip import sync
from hgip.projectclient import ProjectClient
#from multiprocessing import Process

#def group_callback(*args):
#    print 'hgi-project-sync group: ', args 

#DEBUG_LOG_FORMAT = '%(levelname)s:%(asctime)-15s:%(funcname)s:%(message)s'
logging.basicConfig(format='%(levelname)s %(asctime)s %(name)s.%(funcName)s: %(message)s', level=logging.DEBUG)

def main():
    # parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', action='count', dest='verbosity', default=0)
    parser.add_argument('--verbose', action='store', dest='verbosity', default=0, type=int)
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
    config_files = config.read(['/etc/hgi-project.cfg', os.path.expanduser('~/.hgi-project'), 'hgi-project.cfg'])
    _log.info('read configuration from %s' % (config_files))

    cli = ProjectClient(api_home_url=config.get('client', 'api-home-url'), relations=dict(config.items('relations')))
    _log.debug("client: %s" % str(cli))

    projects = cli.projects()
    _log.debug("projects: %s" % str(projects))

    exit()
    # 
    gids = [ 967, 994, 1056, 1082, 1098, 1115, 1118, 1158, 1159, 1163, 1178, 1185, 1195, 1313, 1319, 1320, 1324, 1331, 1332, 1336, 1337, 1338, 1339, 1342, 1344, 1345, 1347, 1349, 1350, 1355, 1360, 1363, 1365, 1376, 1384, 1387, 1396, 1402, 1407, 1417, 1418, 1420, 1421, 1422, 1425, 1426, 1432, 1433, 1434, 1435, 1437, 1439, 1444, 1449 ]
    groupdns = [ 'cn=hgi,ou=group,dc=sanger,dc=ac,dc=uk', 'cn=crohns,ou=group,dc=sanger,dc=ac,dc=uk', 'cn=devxomes,ou=group,dc=sanger,dc=ac,dc=uk' ]


    # prepare LDAP syncrepl query
    user_gid_match = '(%s=%%s)' % (config.get('ldap','user_gid_attr'))
    user_gid_match_filter = '(|' + ''.join([user_gid_match % gid for gid in gids]) + ')'
    _log.debug('using user_gid_match_filter %s' % (user_gid_match_filter))
    
    user_groupdn_match = '(%s=%%s)' % (config.get('ldap','user_memberof_group_attr'))
    user_groupdn_match_filter = '(|' + ''.join([user_groupdn_match % groupdn for groupdn in groupdns]) + ')'
    _log.debug('using user_groupdn_match_filter %s' % (user_groupdn_match_filter))

    group_gid_match = '(%s=%%s)' % (config.get('ldap','group_gid_attr'))
    group_gid_match_filter = '(|' + ''.join([group_gid_match % gid for gid in gids]) + ')'
    _log.debug('using group_gid_match_filter %s' % (group_gid_match_filter))

    usergroup_filter = ''.join([
            # top-level can be either group or user
            '(|',
            # group section
            '(&',
            config.get('ldap', 'group_filter'),
            group_gid_match_filter,
            ')', 
            # user section
            '(&',
            config.get('ldap', 'user_filter'),
            '(|',
            user_gid_match_filter,
            user_groupdn_match_filter,
            ')',
            ')',
            # end of top-level or
            ')',
            ])

    # syncrepl callback closure (over config)
    def usergroup_callback(action='', odn='', dn='', attrs={}):
        print 'hgi-project-sync user: action=%s odn=%s dn=%s attrs=%s config=%s' % (action, odn, dn, attrs, config)

    _log.info('starting sync for usergroup_filter %s' % (usergroup_filter))
    sync.ldap_sync(
        ldap_uri = config.get('ldap','uri'),
        ldap_base_dn = config.get('ldap','base_dn'),
        ldap_filter = usergroup_filter,
        ldap_attrlist = list(set([
                    'dn', 
                    'objectClass',
                    config.get('ldap','group_gid_attr'), 
                    config.get('ldap','group_member_username_attr'), 
                    config.get('ldap','group_groupname_attr'), 
                    config.get('ldap','group_owner_attr'),
                    config.get('ldap','user_gid_attr'), 
                    config.get('ldap','user_username_attr'), 
                    ])),
        callback = usergroup_callback,
        )

    sys.exit(0)


if __name__ == '__main__':
    main()

