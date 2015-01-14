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
import requests
from urlparse import urljoin

class Client:

    def __init__(self, api_home_uri=''):
        self.__log = logging.getLogger(__name__)
        self.__log.debug("Client.__init__")
        # _links is dict of dicts of lists keyed on cur_uri and rel (with list of linked_uris)
        self._links = dict()
        # requests session to persist configuration
        self._s = requests.Session()
        self._s.headers.update({'Accept': 'application/json-home; q=1, application/json; q=0.5, text/html; q=0.3, application/xml; q=0.2, text/xml; q=0.2, text/plain; q=0.1, */*; q=0'})

        r = self._s.get(api_home_uri)
        self.__log.debug("Requested %s with headers=%s" % (api_home_uri, str(r.request.headers)))
        if r.status_code != requests.codes.ok:
            self.__log.error("Response from api_home_uri (%s) not OK: %s" % (api_home_uri, r.status_code))
            r.raise_for_status()
        
        self.__log.debug("Response OK from api_home_uri (%s): content-type=%s, content-length=%s" % (api_home_uri, r.headers['content-type'], r.headers['content-length']))

        if r.links:
            self.__log.debug("Response header included links: %s" % (str(r.links)))
            for key in r.links:
                if 'url' in r.links[key]:
                    linked_url = r.links[key]['url']
                if 'rel' in r.links[key]:
                    rel = r.links[key]['rel']
                if linked_url and rel:
                    self.remember_link(api_home_uri, rel, linked_url)

        # parse content appropriately
        if r.headers['content-type'] in ['application/json-home', 'application/json']:
            # parse JSON home document or other JSON directly
            self._home_data = r.json()
            self.__log.debug("Have JSON home data: %s" % (str(self._home_data)))
            if 'resources' in self._home_data:
                for rel, d in self._home_data['resources'].iteritems():
                    if 'href' in d:
                        self.remember_link(api_home_uri, rel, d['href']) 
        else:
            self.__log.warning("API home returned unknown content-type %s, cannot parse: %s" % (r.headers['content-type'], r.text))
            # TODO: could try to extract links from other content types?

    def remember_link(self, base_url, rel, linked_url):
        if base_url not in self._links:
            self._links[base_url] = dict()
        if rel not in self._links[base_url]:
            self._links[base_url][rel] = []

        linked_url_absolute = urljoin(base_url, linked_url)

        if linked_url_absolute not in self._links[base_url][rel]:
            self._links[base_url][rel].append(linked_url_absolute)

    def list_links(self):
        links = []
        for cur_uri, d in self._links.iteritems():
            for rel, l in d.iteritems():
                for linked_uri in l:
                    links.append("%s --(%s)--> %s" % (cur_uri, rel, linked_uri))
        return links

    def __str__(self):
        return "hgip.Client with links: \n\t%s" % ("\n\t".join(self.list_links()))
    

