all:
	@./venv/citizens/bin/python setup.py sdist
	@mv ./dist/citizens*.tar.gz ./
	@make clean
start:
	@./venv/citizens/bin/python ./citizens/main.py
install:
	@sh ./install.sh
test:
	@./venv/citizens/bin/python ./tests/run.py
clean:
	@rm -rf build
	@rm -rf citizens.egg-info
	@rm -rf dist
	@rm -rf logs
	@rm -f MANIFEST
ammo:
	@./venv/citizens/bin/python ./tests/scripts/data.py
