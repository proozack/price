from app import api
# from .main_page import (HelloWorld, Users, UserEP, LogOut, SignIn, SignUp, Status, Auth, UiRouterNavigation, OfertList)
from .main_page import HelloWorld

import logging
log = logging.getLogger(__name__)


api.add_resource(HelloWorld, '/')
"""
#api.add_resource(Users, '/users')
api.add_resource(Users, '/users')
api.add_resource(UserEP, '/user/<int:ident>')
api.add_resource(LogOut, '/auth-sessions/<string:session_id>')
api.add_resource(SignIn, '/register')
api.add_resource(Auth, '/auth-sessions')
api.add_resource(SignUp, '/signup')
api.add_resource(Status, '/user/<int:ident>/status/<string:status>')
api.add_resource(UiRouterNavigation, '/ui-router-navigation')
api.add_resource(OfertList, '/ofert_list')
"""
