FROM python:3.7

RUN wget -qO - https://www.mongodb.org/static/pgp/server-4.0.asc | apt-key add -; \
	echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-4.0.list; \
	apt-get update; \
	apt-get install -y systemd mongodb-org

RUN mkdir -p /data/db

WORKDIR /app
COPY citizens /app/citizens
COPY citizens.config.json /app/citizens.config.json
COPY requirements.txt /app/requirements.txt
COPY entrypoint.sh /app/entrypoint.sh

RUN pip install -r requirements.txt

EXPOSE 8080
EXPOSE 27017

ENTRYPOINT [ "sh", "/app/entrypoint.sh" ]
