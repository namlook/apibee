#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2011, Nicolas Clairon
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the University of California, Berkeley nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE REGENTS AND CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from restkit import Resource as RestkitResource, RequestFailed

try:
    import simplejson as json
except ImportError:
    import json

class Client(RestkitResource):

    def __init__(self, base_uri, **kwargs):
        super(Client, self).__init__(base_uri, follow_redirect=True, max_follow_redirect=10, **kwargs)
        self._query = []
        self._last_result = None
        self._last_response = None

    def __getattr__(self, key):
        return Resource(self, [key])

    def __getitem__(self, key):
        return Resource(self, [key])

    def request(self, *args, **kwargs):
        resp = super(Client, self).request(*args, **kwargs)
        self._last_response = resp
        self._last_result = resp.body_string()
        return self.process_result(self._last_result)

    def __call__(self, **query):
        query.update(self._query)
        url, query = self.build_request('/', query)
        return self.get(url, **query)

    def build_request(self, resource, query):
        """
        add custom effect to the resouce url and the query params before building the request

        This method should return a tuple (resource_url, query_params):

        ex:
            ('/tests/example', {'foo':bar, 'spam':eggs})
        """
        return resource, query

    def process_result(self, result):
        return result

class Resource(dict):
    def __init__(self, client, resources_list):
        self._client = client
        self._resources = resources_list

    def __getitem__(self, key):
        return Resource(self._client, self._resources+[key])

    def __getattr__(self, key):
        return Resource(self._client, self._resources+[key])

    def __call__(self, **query):
        url = self._get_resource_url()
        query = self._get_query(**query)
        url, query = self._client.build_request(url, query)
        return self._client.get(url, **query)

    def _get_resource_url(self):
        return "/"+"/".join(self._resources)
    
    def _get_query(self, **query):
        query.update(self._client._query)
        return query

