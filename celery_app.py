from localconfig import CeleryApp as cfg
from price import create_app
from price import celery_app

app = create_app(cfg())
app.app_context().push()

