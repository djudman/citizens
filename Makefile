host:=84.201.176.147  # тестовый стенд
# host:=localhost # пригождается для отладки

all:
	@./venv/citizens/bin/python setup.py sdist
	@mv ./dist/citizens*.tar.gz ./
	@make clean
start:
	@./venv/citizens/bin/python ./citizens/__main__.py
install:
	@sh ./install.sh $(host)
test:
	@./venv/citizens/bin/python ./tests/run.py
clean:
	@rm -rf build
	@rm -rf citizens.egg-info
	@rm -rf dist
	@rm -rf logs
	@rm -f MANIFEST
	@rm -f ./tests/yandex-tank/ammo.txt
	@rm -f ./tests/yandex-tank/load.yaml
ammo:
	@./venv/citizens/bin/python ./tests/scripts/yandex-tank/ammo.py --host=$(host)
tank: ammo
	$(shell export CITIZENS_HOST=$(host); envsubst '$$CITIZENS_HOST' < ./tests/scripts/yandex-tank/load.yaml.template > ./tests/scripts/yandex-tank/load.yaml)
	docker run -v $(shell cd ./tests/scripts/yandex-tank && pwd):/var/loadtest -v $SSH_AUTH_SOCK:/ssh-agent -e SSH_AUTH_SOCK=/ssh-agent --net host -it direvius/yandex-tank
request:
	@./venv/citizens/bin/python ./tests/scripts/client.py --host=$(host)
