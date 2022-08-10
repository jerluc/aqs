deps:
	poetry install

build: deps
	rm -rf dist/
	poetry build

test: deps
	poetry run pytest

install: build
	pip install dist/*.whl

.PHONY: deps build
