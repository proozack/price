from celery import Celery
import time

app = Celery('tasks', broker='redis://192.168.254.201:6379/0')

@app.task
def add(x, y):
    time.sleep(5)
    return x + y
