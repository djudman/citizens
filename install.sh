#!/bin/sh

export CITIZENS_SERVER_NAME=84.201.138.48
export CITIZENS_USER=entrant
export CITIZENS_PATH=$(pwd)
export CITIZENS_VENV=$CITIZENS_PATH/venv/citizens

python3 -m venv $CITIZENS_VENV
curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
$CITIZENS_VENV/bin/python /tmp/get-pip.py
rm -f /tmp/get-pip.py

$CITIZENS_VENV/bin/pip install -r requirements.txt

if [ -d "/etc/nginx/conf.d" ]; then
    envsubst '$CITIZENS_SERVER_NAME:$CITIZENS_PATH' < ./configs/nginx.conf > ./configs/citizens.nginx.conf
    sudo ln -sf $CITIZENS_PATH/configs/citizens.nginx.conf /etc/nginx/conf.d/citizens.conf
    sudo service nginx reload
else
    echo "WARNING: nginx not found"
fi

if [ -d "/etc/supervisor/conf.d" ]; then
    mkdir logs
    envsubst '$CITIZENS_USER:$CITIZENS_PATH:$CITIZENS_VENV' < ./configs/supervisor.conf > ./configs/citizens.supervisor.conf
    sudo ln -sf $CITIZENS_PATH/configs/citizens.supervisor.conf /etc/supervisor/conf.d/citizens.conf
    sudo service supervisor reload
else
    echo "WARNING: supervisord not found"
fi
