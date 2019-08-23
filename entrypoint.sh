#!/bin/sh
mongod --bind_ip_all > /var/log/mongodb.stdout &
python citizens/__main__.py
