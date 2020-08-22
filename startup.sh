#!/bin/bash
export FLASK_ENV=development
export FLASK_USER_ID=1
export SECRET_KEY=abcd12345acbbbbbbbbbbaaaaaajjshsjsjsksiwiwiwuwwiiwowoqlq1223124
export SESSION_TYPE=redis
export SESSION_REDIS="redis://:abc1233@127.0.0.1:6379/0"
#export FLASK_APP=wm/wm.py
ENV=price
source $WORKON_HOME/$ENV/bin/activate
env FLASK_APP=app.py flask run --host=0.0.0.0 --port=9999
FLASK_APP=wm:make_shell_context
