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

class RelLink:
    def __init__(self, base_url, rel, linked_url):
        self.base_url = base_url
        self.rel = rel
        self.linked_url = linked_url

class RelLinksMixin: 
    def __init__(self):
        # _links is dict of dicts of lists keyed on cur_uri and rel (with list of linked_uris)
        self._links = dict()

    def remember_link(self, base_url, rel, linked_url):
        if base_url not in self._links:
            self._links[base_url] = dict()
        if rel not in self._links[base_url]:
            self._links[base_url][rel] = []

        linked_url_absolute = urljoin(base_url, linked_url)

        if linked_url_absolute not in self._links[base_url][rel]:
            self._links[base_url][rel].append(linked_url_absolute)

    def list_links(self):
        for cur_uri, d in self._links.iteritems():
            for rel, l in d.iteritems():
                pass

    def list_links(self, base_url):
        if base_url not in self._links:
            return None 
        links = []
        for rel, l in self._links[base_url].iteritems():
            for linked_uri in l:
                links.append("%s --(%s)--> %s" % (base_url, rel, linked_uri))
        return links
            
        return self._links[base_url][rel]

    def list_links(self, base_url, rel):
        if base_url not in self._links:
            return None
        if rel not in self._links[base_url]:
            return None
        return self._links[base_url][rel]

    def __str__(self):
        return "%s with links: \n\t%s" % (__name__, "\n\t".join(self.list_links()) or "none")

       

class RestClient(RelLinksMixin):

    def __init__(self, relations={}):
        self.__log = logging.getLogger(__name__)
        self.__log.debug("__init__(relations=%s)" % (str(relations)))

        # _content_handlers is a dict mapping content-types to handler functions
        self._content_handlers = dict()
        
        # _relations contains known link relations
        self._relations = relations


        # requests session to persist configuration
        self._session = requests.Session()

    @property
    def accept(self):
        accepts = []
        for content_type in self._content_handlers:
            max_qvalue = sorted(self._content_handlers[content_type], reverse=True)[0]
            if self.qvalue_nearly_0(max_qvalue):
                max_qvalue = "0"
            else:
                max_qvalue = ("%.7f" % max_qvalue).rstrip('0').rstrip('.')
            accepts.append("%s; q=%s" % (content_type, max_qvalue))
        return ", ".join(accepts)

    @staticmethod
    def qvalue_nearly_0(qvalue):
        return abs(qvalue) < 0.0000001

    def get(self, url):
        # Build accept header from _content_handlers
        self._session.headers.update({'Accept': self.accept})

        r = self._session.get(url)
        self.__log.debug("Requested %s with headers=%s" % (url, str(r.request.headers)))
        if r.status_code != requests.codes.ok:
            self.__log.error("Response from url (%s) not OK: %s" % (r.url, r.status_code))
            r.raise_for_status()
        self.__log.debug("Response OK from url (%s): content-type=%s, content-length=%s" % (r.url, r.headers['content-type'], r.headers['content-length']))

        if r.links:
            self.__log.debug("Response header included links: %s" % (str(r.links)))
            for key in r.links:
                if 'url' in r.links[key]:
                    linked_url = r.links[key]['url']
                if 'rel' in r.links[key]:
                    rel = r.links[key]['rel']
                if linked_url and rel:
                    self.remember_link(r.url, rel, linked_url)

        # dispatch to appropriate content handler 
        content_type = r.headers['content-type']
        if content_type in self._content_handlers:
            self.__log.debug("Have content handlers for content-type %s: %s" % (content_type, str(self._content_handlers[content_type])))
            # sort by qvalue
            handled=False
            for qvalue in sorted(self._content_handlers[content_type], reverse=True):
                if self.qvalue_nearly_0(qvalue):
                    # qvalue is 0 (or nearly so), this is not acceptable to the handler
                    break
                self.__log.debug("Trying %d content handlers for content-type %s at qvalue %f: %s" % (len(self._content_handlers[content_type][qvalue]), content_type, qvalue, str(self._content_handlers[content_type][qvalue])))
                # try each content_handler in turn and break on success
                for content_handler in self._content_handlers[content_type][qvalue]:
                    handled = content_handler(self, r)
                    if handled:
                        break
                if handled:
                    break
            if not handled:
                self.__log.warning("No handler was able to successfully handle the response (content-type %s), data: %s" % (content_type, str(r.text)))
        else:
            self.__log.warning("No handler registered for content-type %s (have handlers for: %s)" % (content_type, str(self._content_handlers)))

 
    def handle_content_type(self, content_type, qvalue):
        """Clients must implement content handlers and decorate them using this method.
        
        Two arguments are passed to the content handler function:
          * The client object
          * The requests.response object 

        The content handler must return either True or False depending on whether it 
        successfully handled the content (if it returns False, the next content handler 
        will be tried until one returns true). If there are multiple content handlers 
        for a given content-type, they will be tried in order of their qvalues from 
        highest to lowest (except for 0, which indicates not acceptable). If multiple 
        handlers have the same qvalue, the order in which content handlers are 
        declared will determines the order in which they will be tried.
        
        The decorator itself takes two arguments:
          * The content-type which it is prepared to handle
          * The "quality" (qvalue) for that content-type
            ranging from 0.0 (not acceptable) to 1.0 (ideal)

        Multiple decorators can be applied to the same function to indicate that it 
        can handle all of them. 
          
        Ex::
            cli = Client()
            @cli.handle_content_type('application/json-home', 1.0)
            def json_home_handler(client, response):
                print "JSON Home handled!"
                return True
        """
        def decorator(func): 
            self.__log.debug("handle_content_type decorator invoked for content_type=%s" % content_type)
            if content_type not in self._content_handlers:
                self._content_handlers[content_type] = dict()
            if qvalue not in self._content_handlers[content_type]:
                self._content_handlers[content_type][qvalue] = []
            if func not in self._content_handlers[content_type][qvalue]:
                self.__log.debug("registering function %s as handler for content-type %s at qvalue %f" % (func.__name__, content_type, qvalue))
                self._content_handlers[content_type][qvalue].append(func)
            def wrapper(*args, **kwargs):
                self.__log.debug("handle_content_type wrapper invoked for content_type=%s" % content_type)
                func(*args, **kwargs)
            return wrapper
        return decorator




    

