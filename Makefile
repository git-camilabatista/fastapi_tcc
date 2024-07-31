POETRY_RUN = poetry run

fastapi:
	$(POETRY_RUN) uvicorn fastapi_tcc.main:app --port 8001