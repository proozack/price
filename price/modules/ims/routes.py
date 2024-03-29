from price import api
# from .main_page import (HelloWorld, Users, UserEP, LogOut,
# SignIn, SignUp, Status, Auth, UiRouterNavigation, OfertList)
from .main_page import (CategoryView, ProductView, ShopsStats, Imports, DtImports, Tags, DtTags, Tag, EntryPoint)

import logging
log = logging.getLogger(__name__)


api.add_resource(CategoryView, '/category/<string:category>/<int:page>')
api.add_resource(ProductView, '/product/<int:product>')
api.add_resource(ShopsStats, '/shops')
api.add_resource(Imports, '/imports')
api.add_resource(Tags, '/tags')
api.add_resource(Tag, '/tag/<string:tag>')
api.add_resource(DtImports, '/dt_imports')
api.add_resource(DtTags, '/dt_tags')
api.add_resource(EntryPoint, '/entry_point/<int:entry_point_id>/<int:page>')

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
