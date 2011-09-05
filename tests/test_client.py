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

import unittest
from apibee import Client, RequestFailed
import json

TEST_SERVER = "http://localhost:8080"

class ClientTestCase(unittest.TestCase):

    def test_simple(self):
        """
        /tests/simple
        """
        api = Client(TEST_SERVER)
        result = api.tests.simple()
        self.assertEqual(result, "simple test")

    def test_with_args(self):
        """
        /tests/with_args?foo=1&bar=2
        """
        api = Client(TEST_SERVER)
        result = api.tests.with_args(foo="1", bar="2")
        self.assertEqual(result, '{"foo": "1", "bar": "2"}')

    def test_persistent_params(self):
        """
        add foo=42 for each request
        /tests/with_args?bar=2
        """
        class Api(Client):

            def set_persistent_query(self, **args):
                self._persistent_query = args

            def build_request(self, resource, query):
                query.update(self._persistent_query)
                return resource, query

        api = Api(TEST_SERVER)
        result = api.tests.with_args(bar="2")
        self.assertEqual(result, '{"foo": null, "bar": "2"}')
        api.set_persistent_query(foo=42)
        result = api.tests.with_args(bar="2")
        self.assertEqual(result, '{"foo": "42", "bar": "2"}')
        result = api.tests.with_args(bar="3")
        self.assertEqual(result, '{"foo": "42", "bar": "3"}')

    def test_get_object(self):
        """
        /tests/get_object/23
        """
        api = Client(TEST_SERVER)
        result = api.tests.get_object["23"]()
        self.assertEqual(result, '{"id": "23"}')

    def test_end_resources(self):
        """
        /tests/list.json?foo=bar
        /tests/list.xml?foo=bar
        """
        class Api(Client):
            def set_format(self, fmt):
                self._format = fmt
            def build_request(self, resource, query):
                resource = "%s.%s" % (resource, self._format)
                return resource, query

        api = Api(TEST_SERVER)
        api.set_format("json")
        result = api.tests.list(foo="bar")
        self.assertEqual(result, 'bar')
        self.assertEqual(api._last_response.final_url, TEST_SERVER+"/tests/list.json?foo=bar")
        api.set_format("xml")
        result = api.tests.list(foo="arg")
        self.assertEqual(api._last_response.final_url, TEST_SERVER+"/tests/list.xml?foo=arg")

    def test_send_json_query(self):
        """
        /test/jsonquery?q='{"eggs":"spam", "foo":"bar"}'
        """
        class JsonClient(Client):
            def process_result(self, result):
                return json.loads(result)

        q = dict(foo="bar", eggs="spam")
        jsonapi = JsonClient(TEST_SERVER)
        self.assertEqual(q, jsonapi.tests.jsonquery(q=json.dumps(q)))

        class ApiJsonClient(JsonClient):
            def build_request(self, resource, query):
                query = {"q": json.dumps(query)}
                return resource, query

        jsonapi = ApiJsonClient(TEST_SERVER)
        self.assertEqual(q, jsonapi.tests.jsonquery(**q))
        self.assertEqual(jsonapi._last_response.final_url, TEST_SERVER+"/tests/jsonquery?q=%7B%22eggs%22%3A+%22spam%22%2C+%22foo%22%3A+%22bar%22%7D")

    def test_send_json_query_with_persistent_params(self):
        """
        /test/jsonquery?q='{"eggs":"spam", "foo":"bar"}'&v=1.0
        """
        class JsonClient(Client):

            def build_request(self, resource, query):
                query = {"q": json.dumps(query)}
                query.update(self._persistent_query)
                return resource, query

            def process_result(self, result):
                return json.loads(result)


        jsonapi = JsonClient(TEST_SERVER)
        q = dict(foo="bar", eggs="spam")
        jsonapi._persistent_query = dict(v=1.0)
        self.assertEqual(q, jsonapi.tests.jsonquery(**q))
        self.assertEqual(jsonapi._last_response.final_url, TEST_SERVER+"/tests/jsonquery?q=%7B%22eggs%22%3A+%22spam%22%2C+%22foo%22%3A+%22bar%22%7D&v=1.0")
