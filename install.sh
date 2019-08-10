#!/bin/sh

export CITIZENS_SERVER_NAME=84.201.138.48
export CITIZENS_USER=entrant
export CITIZENS_PATH=$(pwd)

python3.7 -m venv ./venv/citizens
curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
./venv/citizens/bin/python /tmp/get-pip.py
rm -f /tmp/get-pip.py

./venv/citizens/bin/pip install -r requirements.txt

if [ -d "/etc/nginx/conf.d" ]; then
    envsubst < ./configs/nginx.conf > ./configs/citizens.nginx.conf
    ln -s ./configs/citizens.nginx.conf /etc/nginx/conf.d/citizens.conf
    sudo service nginx reload
else
    echo "WARNING: nginx not found"
fi

if [ -d "/etc/supervisor/conf.d" ]; then
    envsubst < ./configs/supervisor.conf > ./configs/citizens.supervisor.conf
    ln -s ./configs/citizens.supervisor.conf /etc/supervisor/conf.d/citizens.conf
    sudo service supervisor reload
else
    echo "WARNING: supervisord not found"
fi
