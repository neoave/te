# Preparation

TMP = $(CURDIR)/tmp
VERSION = $(shell grep ^Version te.spec | sed 's/.* //')
PACKAGE = te-$(VERSION)
FILES = LICENSE README.md \
		Makefile requirements.txt setup.py te.spec \
		files playbooks scripts src tests

# Formating
format:
	black src
	black tests
	black setup.py
	isort src
	isort tests
	isort setup.py

# Testing
tox:
	tox

test: venv
	. .env/bin/activate; .env/bin/pytest tests/unit


# Python development in venv
venv: .env/touchfile

.env/touchfile: requirements.txt test-requirements.txt
	test -d .env || virtualenv .env
	. .env/bin/activate; pip3 install -Ur requirements.txt
	. .env/bin/activate; pip3 install -Ur test-requirements.txt
	touch .env/touchfile

# Docs
docs:
	cd docs && make html

tmp:
	mkdir -p $(TMP)

# Package build
source: clean tmp
	mkdir -p $(TMP)/SOURCES
	mkdir -p $(TMP)/$(PACKAGE)
	cp -a $(FILES) $(TMP)/$(PACKAGE)

tarball: source
	cd $(TMP) && tar cfz SOURCES/$(PACKAGE).tar.gz $(PACKAGE)
	@echo ./tmp/SOURCES/$(PACKAGE).tar.gz

rpm: tarball
	rpmbuild --define '_topdir $(TMP)' -bb te.spec

srpm: tarball
	rpmbuild --define '_topdir $(TMP)' -bs te.spec

rpms: rpm srpm

# Cleanup
clean:
	rm -rf build dist .cache .tox .mypy_cache .pytest_cache $(TMP) docs/_build

clean-all: clean
	rm -rf .env
