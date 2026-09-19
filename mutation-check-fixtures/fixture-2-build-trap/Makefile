PYTHON ?= python3

build:
	@mkdir -p build && cp src/tempconv.py build/tempconv.py && echo "built"

test: build
	@$(PYTHON) -m pytest -q

.PHONY: build test
