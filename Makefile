.PHONY: help clean lint test docs serve release bump
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys
from urllib.request import pathname2url
webbrowser.open("file:" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define BUMP_SCRIPT
import os, prettyqt
version = prettyqt.__version__
os.system(f'cz changelog --unreleased-version "v{version}"')
endef
export BUMP_SCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

clean: ## remove all build, test, coverage and Python artifacts
	git clean -dfX

test: ## run tests
	hatch run test

mypy: ## run mypy type checking
	hatch run lint-check

docs: ## builds the documentation
	hatch run docs-build
	$(BROWSER) site/index.html

serve: ## run html server watching file changes in realtime
	hatch run docs-serve
