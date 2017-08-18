# .DEFAULT_GOAL :=
# .RECIPEPREFIX = "    "


.PHONY: plural dist tests pip docs

all: clean tests

pip:
	@pip install --disable-pip-version-check --no-cache-dir -U pip
	@pip install --no-cache-dir -r development.txt


tests: unit functional

unit:
	@nosetests tests/unit

functional:
	@nosetests tests/functional

docs:
	cd docs && make html

clean:
	@find . -name '*.pyc' -delete
	@find . -name '#*' -delete


release:
	@rm -rf dist/*
	@./.release
	@python setup.py build sdist
	@twine upload dist/*.tar.gz


numbers:
	@python nums.py


docker_image:
	@docker build -t plural .
