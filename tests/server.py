from bottle import route, run, request
import json

@route('/tests/simple')
def simple():
    return "simple test"

@route('/tests/with_args')
def with_args():
    foo =  request.GET.get('foo')
    bar =  request.GET.get('bar')
    return json.dumps({'foo': foo, 'bar': bar})

@route('/tests/list.json')
@route('/tests/list.xml')
def list_json():
    foo = request.GET.get('foo')
    return foo

@route('/tests/get_object/:id')
def get_object(id):
    return json.dumps({'id': id})

@route('/tests/jsonquery')
def jsonquery():
    return json.dumps(json.loads(request.GET.get('q')))

run(host='localhost', port=8080)

