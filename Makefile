test:
	python -B -m unittest discover

lint:
	@flake8 && echo "Static Check Without Error"

coverage:
	@coverage run --source=microproxy -m unittest discover

install:
	pip install -U --no-deps .

install-all:
	pip install -U .
	pip install -U .[viewer]
	pip install -U .[develop]

run-server:
	mpserver --config-file conf/application.cfg --log-config-file conf/logging.cfg
