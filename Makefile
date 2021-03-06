.PHONY: clean-pyc clean-build docs

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "testall - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "sdist - package"

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

lint:
	flake8 --exclude=migrations mailchimper functional_tests

test:
	python project_template/manage.py test mailchimper

test-ft:
	python project_template/manage.py test functional_tests

test-tox:
	tox

test-tox-ft:
	tox -e py26-django16-ft,py27-django16-ft,py33-django16-ft

coverage-console:
	coverage run --source mailchimper --omit=mailchimper/migrations/*,*/tests/factories.py,mailchimper/management/* project_template/manage.py test mailchimper
	coverage report -m

coverage: coverage-console
	coverage html
	open htmlcov/index.html

docs:
	rm -f docs/mezzanine_mailchimper.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ mezzanine_mailchimper
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html

release: clean
	python setup.py sdist upload
	python setup.py bdist_wheel upload

sdist: clean
	python setup.py sdist
	ls -l dist
