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
import logging
from restclient import RestClient

default_link_rel_users = "http://hgi.sanger.ac.uk/rel/users"
default_link_rel_projects = "http://hgi.sanger.ac.uk/rel/projects"


class ProjectClient:

    def __init__(self, api_home_url='', relations={}):
        self.__log = logging.getLogger(__name__)
        self.__log.debug("__init__(api_home_url=%s, relations=%s)" % (api_home_url, str(relations)))

        self._rc = RestClient(relations)

        @self._rc.handle_content_type('application/json-home', 0.75)
        def handle_json_home0(client, resp):
                # parse JSON home document or other JSON directly
                json_home_data = resp.json()
                self.__log.debug("have JSON home data: %s" % (str(json_home_data)))
                if 'resources' in json_home_data:
                    for rel, d in json_home_data['resources'].iteritems():
                        if 'href' in d:
                            client.remember_link(resp.url, rel, d['href']) 
                    return True
                else:
                    return False

        # Fetch and handle the API Home URL
        self._rc.get(api_home_url)


    def __str__(self):
        return "%s with RestClient: %s" % (__name__, str(self._rc))



    

