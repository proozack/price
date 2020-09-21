#!/usr/bin/env python3
import logging
from flask_script import Manager
from app import create_app
from app.modules.ims.models import Image

app = create_app()
log = logging.getLogger(__name__)

manager = Manager(app)


@manager.command
def enrich_image(abc, cba):
    print("hello {} -> {}".format(abc, cba))


if __name__ == "__main__":
    manager.run()
