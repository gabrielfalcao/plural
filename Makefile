# .DEFAULT_GOAL :=
# .RECIPEPREFIX = "    "


.PHONY: gitgraph dist tests pip

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
