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
    return request.GET.get('foo')

@route('/tests/get_object/:id')
def get_object(id):
    return json.dumps({'id': id})

@route('/tests/jsonquery')
def jsonquery():
    return json.dumps(json.loads(request.GET.get('q')))


@route('/tests/simple_post', method='POST')
def simple_post():
    return json.dumps({'test': request.POST.get('test')})

@route('/test/post_with_args/:id', method='POST')
def post_with_args(id):
    return json.dumps({'id': id, 'test': request.POST.get('test')})

@route('/tests/simple_delete', method='DELETE')
def simple_delete():
    print request.GET.get('test')
    return json.dumps({'test': request.GET.get('test')})

run(host='localhost', port=8080)

