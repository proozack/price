from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from wm import create_app
from app import db
#from conf.localconfig import Config

app = create_app()

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
