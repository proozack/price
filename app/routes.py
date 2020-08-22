#from app import app
from flask_restful import Resource, Api
from app.modules.ims.models import User
#from app.modules.ims.models import ArchUser
from flask import session

from app import api


"""
@app.route('/')
@app.route('/index')
def index():
    u = User.query.all()
    lista = []
    for c in u:
        lista.append(c.name)
    return "Hello, World! %r"%(lista,)
"""

"""
@app.route('/test')
def test():
    return session.get('name')
"""


