build:
	@python3 -m build

test:
	@coverage run -m pytest

install:
	@python3 -m pip install .

dist:
	@twine upload dist/* --skip-existing

.PHONY: build test dist
