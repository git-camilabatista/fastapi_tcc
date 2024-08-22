POETRY_RUN = poetry run

fastapi:
	$(POETRY_RUN) uvicorn fastapi_tcc.main:app --host 192.168.0.19 --port 8001

#* Formatters
.PHONY: format
format:
	@poetry run ruff format .

#* Linting
.PHONY: lint
lint:
	@poetry run ruff check .
	@poetry run ruff format --check .