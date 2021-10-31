from price.extension import api


from price.modules.hello_world.test import HelloWorld

api.add_resource(HelloWorld, '/hello_world')

