all:
	python3 ./citizens/main.py
install:
	pip install -r requirements.txt
test:
	cd tests && python run.py
