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
import logging
import ldap
import ldap.syncrepl
import time
import exceptions
import anydbm

class LDAPSync(ldap.ldapobject.LDAPObject, ldap.syncrepl.SyncreplConsumer):

    def __init__(self, *args, **kwargs):
        self.__log = logging.getLogger(__name__)
        self.__log.debug("LDAPSync.__init__")
        ldap.ldapobject.LDAPObject.__init__(self, *args, **kwargs)
        self.__db = anydbm.open('/tmp/testdb.dbm', 'c', 0640)
        self.__presentUUIDs = {}

    def syncrepl_set_cookie(self,cookie):
        self.__log.debug("LDAPSync.syncrepl_set_cookie. cookie=" + cookie)
        self.__db['cookie'] = cookie

    def syncrepl_get_cookie(self):
        self.__log.debug("LDAPSync.syncrepl_get_cookie")
        if 'cookie' in self.__db:
            self.__log.debug("Returning cookie: " + self.__db['cookie'])
            return self.__db['cookie']

    def syncrepl_delete(self, uuids):
        self.__log.debug("LDAPSync.syncrepl_delete. uuids=" + str(uuids))
        for uuid in uuids:
            dn = self.__db[uuid]
            print "delete %s" % dn
            del self.__db[uuid]

    def syncrepl_present(self, uuids, refreshDeletes=False):
        self.__log.debug("LDAPSync.syncrepl_present. uuids=" + str(uuids) + " refreshDeletes=" + str(refreshDeletes))
        if uuids is None:
            if refreshDeletes is False:
                nonpresent = []
                for uuid in self.__db.keys():
                    if uuid == 'cookie': continue
                    if uuid in self.__presentUUIDs: continue
                    nonpresent.append(uuid)
                self.syncrepl_delete(nonpresent)
            self.__presentUUIDs = {}
        else:
            for uuid in uuids:
                self.__presentUUIDs[uuid] = True

    def syncrepl_entry(self, dn, attrs, uuid):
        self.__log.debug("LDAPSync.syncrepl_entry. dn=" + dn + " attrs=" + str(attrs) + " uuid=" + uuid)
        if uuid in self.__db:
            odn = self.__db[uuid]
            if odn != dn:
                print "moddn %s -> %s" % ( odn, dn )
            else:
                print "modify %s" % self.__db[uuid]
        else:
            print "add %s" % dn
        self.__db[uuid] = dn



def Sync(ldap_uri = 'ldap://localhost', 
         group_base_dn = '', 
         group_filter = '', 
         group_search_fmt = '(cn=%s)',
         group_member_uid_attribute = 'memberUid',
         user_base_dn = '',
         user_search_uid_fmt = '(uid=%s)',
         ):
    _log = logging.getLogger(__name__)

    _log.debug("Sync(): ")

    ldap_sync_conn = LDAPSync(ldap_uri)

    _log.debug("hgi-project-sync: " + str(ldap_sync_conn))

    try:
        ldap_sync_conn.simple_bind_s()
    except ldap.INVALID_CREDENTIALS as e:
        _log.error('Simple bind failed: ' + str(e))
        raise Exception('LDAP bind failed');

    msgid = ldap_sync_conn.syncrepl_search(
        group_base_dn, 
        ldap.SCOPE_SUBTREE, 
        cookie = None, 
        mode = 'refreshAndPersist',
        filterstr = group_filter, 
        )

    try:
        while ldap_sync_conn.syncrepl_poll(all=1, msgid=msgid):
            time.sleep(0.5)
            _log.debug('Polling for syncrepl updates...')
    except KeyboardInterrupt:
        pass

