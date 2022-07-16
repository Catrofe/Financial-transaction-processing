FROM python:3.10
ENV PYTHONUNBUFFERED 1

RUN mkdir /ICEBERG_API
WORKDIR /ICEBERG_API

COPY pyproject.toml /ICEBERG_API/
RUN pip install poetry
RUN poetry install
COPY app /ICEBERG_API/app
CMD ["poetry", "run", "uvicorn", "--host", "0.0.0.0", "app.main:app"]
