dev:
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "ERROR: You must activate a Python virtual environment first."; \
		exit 1; \
	fi
	pip install git+https://github.com/MGabeD/cli_git_changelog.git@v2.0.0
	python -m pip install -e .
