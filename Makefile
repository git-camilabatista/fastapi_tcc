POETRY_RUN = poetry run

fastapi:
	$(POETRY_RUN) uvicorn fastapi_tcc.main:app --host 192.168.0.19 --port 8001