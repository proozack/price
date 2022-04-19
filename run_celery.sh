#!/bin/bash
export FLASK_ENV=development
export FLASK_USER_ID=1
export SECRET_KEY=abcd12345acbbbbbbbbbbaaaaaajjshsjsjsksiwiwiwuwwiiwowoqlq1223124
export SESSION_TYPE=redis
export SESSION_REDIS="redis://:abc1233@127.0.0.1:6379/0"
#export FLASK_APP=wm/wm.py
ENV=price

# echo $1

# celery -A celery_app.celery_app worker -l warning --concurrency=2
celery -A celery_app.celery_app worker -l info --concurrency=1
