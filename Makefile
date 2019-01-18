init:
	pip install pipenv
	pipenv install --dev

test:
	pipenv run py.test tests
	pipenv run py.test --cov=itree tests

clean: build-clean dist-clean

build-clean:
	rm -rf build

dist-clean:
	rm -rf dist

sdist: dist-clean setup.py
	python3 setup.py sdist bdist_wheel

twine-test-upload: sdist
	twine upload  --repository-url https://test.pypi.org/legacy/  dist/*

twine-upload: sdist
	twine upload dist/*

.PHONY: init test sdist twine-test-upload twine-upload clean build-clean dist-clean
