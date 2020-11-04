PYTHON_MAJOR_MINOR := $(shell python -c "import sys; print('{0}{1}'.format(*sys.version_info))")
REQUIREMENTS_TXT = requirements$(PYTHON_MAJOR_MINOR).txt

.PHONY: core-requirements
core-requirements:
	pip install pip setuptools pip-tools

.PHONY: update-requirements
update-requirements: core-requirements
	pip install -U pip setuptools pip-tools
	pip-compile -U requirements.in -o $(REQUIREMENTS_TXT)

.PHONY: requirements
requirements: core-requirements
	pip-sync $(REQUIREMENTS_TXT)

.PHONY: clean-pyc
clean-pyc: requirements
	find . -iname "*.pyc" -delete
	find . -iname __pycache__ | xargs rm -rf

.PHONY: tox-update-requirements
tox-update-requirements: clean-pyc
	tox -c tox-requirements.ini

.PHONY: develop
develop: clean-pyc
	python setup.py develop

.PHONY: check
check: develop
	python manage.py check

.PHONY: migrate
migrate: check
	python manage.py migrate --noinput

.PHONY: runserver
runserver: migrate
	python manage.py runserver

reports:
	mkdir -p $@

.PHONY: pycodestyle
pycodestyle: reports requirements
	set -o pipefail && $@ | tee reports/$@.report

.PHONY: pep8
pep8: pycodestyle

.PHONY: flake8
flake8: reports requirements
	set -o pipefail && $@ | tee reports/$@.report

.PHONY: check8
check8: pycodestyle flake8

.PHONY: clean-coverage
clean-coverage:
	rm -f .coverage

.PHONY: test
test: clean-pyc clean-coverage
	python setup.py test

.PHONY: clean-tox
clean-tox:
	rm -rf .tox

.PHONY: tox
tox: clean-pyc
	tox

.PHONY: clean-all
clean-all: clean-pyc clean-coverage clean-tox
	rm -rf *.egg-info .eggs .cache .coverage build reports

.PHONY: bump-major
bump-major: requirements
	bumpversion major

.PHONY: bump-minor
bump-minor: requirements
	bumpversion minor

.PHONY: bump-patch
bump-patch: requirements
	bumpversion patch

.PHONY: docs
docs: requirements
	python setup.py build_sphinx

.PHONY: dev-build
dev-build: requirements clean-pyc clean-coverage
	python setup.py dev_build

.PHONY: release-build
release-build: requirements clean-pyc clean-coverage
	python setup.py release_build

.PHONY: ship-it
ship-it: requirements clean-pyc clean-coverage
	python setup.py ship_it
