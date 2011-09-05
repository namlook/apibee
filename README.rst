ApiBee
======

ApiBee is a dynamic rest client built on top of the excellent restkit_ library.

.. _restkit : http://github.com/benoitc/restkit

It aims to be able to handle any uris for any apis.

How it work ?
-------------

Let's say we want to fetch the json API of the great service http://www.example.com. Their api is served from http://api.example.com/1.0/::

    >>> from apibee import Client
    >>> api = Client('http://api.example.com/1.0/')

Now we want to get the result from http://api.example.com/1.0/users/search?q=Timy::

    >>> results = api.users.search(q='Timy')

That's it !

Going further
-------------

Getting json result
+++++++++++++++++++

Here::

    class ExampleClient(Client):
        def process_result(self, result):
            return json.loads(result)

Now the result is a python type::

    >>> api = ExampleClient("http://api.example.com/1.0/")
    >>> result = api.user.search(q="timy")

Adding query automatically
++++++++++++++++++++++++++

Sometimes some api are a bit tricky. And we need to build a custom client to match thoses. 

Previously, the version of the api was part of the resource but what if we have to specify it for each request::

    http://api.example.com/user/search?v=1.0&q=Timy

We can specify one or more params which will be automatically add to the query::

    class ExampleClient(Client):
        def set_persistent_query(**args):
            self._persistent_query = args

        def build_query(self, response, query):
            query.update(self._persistent_query)
            return response, query

    >>> api = ExampleClient('http://api.example.com')
    >>> api.set_persistent_query(v="1.0")


Customize resources
+++++++++++++++++++

Some apis like Twitter add `.json` after the resource but before the query : https://api.twitter.com/1/search.json&q=Timy. We can do it like this::

    class TwitterClient(Client):
        def set_format(self, f):
            self._format = f

        def build_query(self, response, query):
            response = "%s.%s" % (response, self._format)
            return response, query

    >>> api = TwitterClient('https://api.twitter.com/1', end_resource='.json')
    >>> results = api.search(q='Timy')

Raising errors
++++++++++++++

Sometimes you may have to clean up the result before send it back. You can do it by overloading the `Client.process_result` method.

Example:

    Google's web service won't send an http error 400 if the request failed. Instead, it will send a custom result::

        http://ajax.googleapis.com/ajax/services/search/web?q=Earth%20Day

will send back::

    {"responseData": null, "responseDetails": "invalid version", "responseStatus": 400}

Let's say we want to catch the error and raise an RequestFailed exception with a custom message which is in the "responseDetails" field::

        class GoogleClient(Client):
            def process_result(self, result):
                if result["responseStatus"] == 400:
                    raise RequestFailed(result['responseDetails'])
                return result

That's it ! Don't forget to return the result at the end of the `process_result` method.

        >>> api = GoogleClient('http://ajax.googleapis.com/ajax/services')
        >>> api.search.web(q="toto")
        Traceback (most recent call last):
        ...
        RequestFailed: invalid version

