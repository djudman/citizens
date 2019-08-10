all:
	@./venv/citizens/bin/python setup.py sdist
start:
	@./venv/citizens/bin/python ./citizens/main.py
install:
	@sh ./install.sh
test:
	@./venv/citizens/bin/python ./tests/run.py
