import functools
import json
from flask import jsonify

def to_json(f):

    @functools.wraps(f)
    def inner(*a, **k):
        #return json.dumps(f(*a, **k))
        return jsonify(f(*a, **k))
    return inner
