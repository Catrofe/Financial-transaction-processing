import asyncio

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine

from src.app import create_app
from src.database import Transaction
from src.settings import Settings

db_url = "sqlite+aiosqlite:///tests/db.sqlite"


@pytest.fixture
def db() -> None:
    async def _setup():
        engine = create_async_engine(db_url, echo=False)
        async with engine.connect() as conn:
            await conn.run_sync(Transaction.metadata.drop_all)
            await conn.run_sync(Transaction.metadata.create_all)

    asyncio.run(_setup())


@pytest.fixture
def app(db: None) -> FastAPI:
    return create_app(Settings(db_url=db_url))


def create_transaction(app_function: FastAPI):
    with TestClient(app_function) as client:
        body = {
            "client_id": 1,
            "transaction_timestamp": "2022-07-13T03:40:23.123Z",
            "value": 10.17,
            "description": "string",
        }

        client.post("/transaction", json=body)


def test_create_transaction_should_success(app: FastAPI):
    with TestClient(app) as client:
        body = {
            "client_id": 1,
            "transaction_timestamp": "2022-07-13T03:40:23.123Z",
            "value": 10.17,
            "description": "string",
        }

        response = client.post("/transaction", json=body)

        assert response.status_code == 201
        assert response.json() == {
            "transaction_id": 1,
            "message": "TRANSACTION_CREATED",
        }


def test_create_transaction_value_as_integer(app: FastAPI):
    with TestClient(app) as client:
        body = {
            "client_id": 1,
            "transaction_timestamp": "2022-07-13T03:40:23.123Z",
            "value": 10,
            "description": "string",
        }

        response = client.post("/transaction", json=body)

        assert response.status_code == 201
        assert response.json() == {
            "transaction_id": 1,
            "message": "TRANSACTION_CREATED",
        }


def test_create_transaction_value_cents(app: FastAPI):
    with TestClient(app) as client:
        body = {
            "client_id": 1,
            "transaction_timestamp": "2022-07-13T03:40:23.123Z",
            "value": 0.99,
            "description": "string",
        }

        response = client.post("/transaction", json=body)

        assert response.status_code == 201
        assert response.json() == {
            "transaction_id": 1,
            "message": "TRANSACTION_CREATED",
        }


def test_create_transaction_value_negative(app: FastAPI):
    with TestClient(app) as client:
        body = {
            "client_id": 1,
            "transaction_timestamp": "2022-07-13T03:40:23.123Z",
            "value": -10.17,
            "description": "string",
        }

        response = client.post("/transaction", json=body)

        assert response.status_code == 400
        assert response.json() == {"detail": "VALUE_MUST_BE_POSITIVE"}


def test_get_balance_should_success(app: FastAPI):
    with TestClient(app) as client:

        create_transaction(app)

        response = client.get("/transaction/1")

        assert response.status_code == 200
        assert response.json() == {"balance": 10.17}


def test_get_balance_should_404(app: FastAPI):
    with TestClient(app) as client:

        create_transaction(app)

        response = client.get("/transaction/-1")

        assert response.status_code == 404
        assert response.json() == {"detail": "NO_VALUE_FOUND_FOR_THESE_PARAMETERS"}


def test_create_two_transactions_should_sum_transaction(app: FastAPI):
    with TestClient(app) as client:
        create_transaction(app)
        create_transaction(app)

        response = client.get("/transaction/1")

        assert response.status_code == 200
        assert response.json() == {"balance": 20.34}


def test_get_transaction_period_should_success(app: FastAPI):
    with TestClient(app) as client:
        create_transaction(app)
        create_transaction(app)

        response = client.get(
            "/transaction/1/2022-07-13T03:40:23.123Z/2022-07-14T03:40:23.123Z"
        )

        assert response.status_code == 200
        assert response.json() == {"balance": 20.34}


def test_get_transaction_in_period_should_success(app: FastAPI):

    with TestClient(app) as client:
        body = {
            "client_id": 1,
            "transaction_timestamp": "2022-07-15T03:40:23.123Z",
            "value": 10.17,
            "description": "string",
        }
        client.post("/transaction", json=body)

        create_transaction(app)

        response = client.get(
            "/transaction/1/2022-07-13T03:40:23.123Z/2022-07-14T03:40:23.123Z"
        )

        assert response.status_code == 200
        assert response.json() == {"balance": 10.17}


def test_get_transaction_period_incorrect_should_404(app: FastAPI):
    with TestClient(app) as client:
        create_transaction(app)

        response = client.get(
            "/transaction/1/2022-07-10T03:40:23.123Z/2022-07-11T03:40:23.123Z"
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "NO_VALUE_FOUND_FOR_THESE_PARAMETERS"}


def test_get_transaction_id_incorrect_should_404(app: FastAPI):
    with TestClient(app) as client:
        create_transaction(app)

        response = client.get(
            "/transaction/2/2022-07-12T03:40:23.123Z/2022-07-14T03:40:23.123Z"
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "NO_VALUE_FOUND_FOR_THESE_PARAMETERS"}


def test_get_transaction_id_incorrect_should_422_pydantic(app: FastAPI):
    with TestClient(app) as client:
        create_transaction(app)

        response = client.get("/transaction/2/2022-07-12T03:40:23.123Z/''")
        assert response.status_code == 422


def test_get_historic_transactions_should_succes(app: FastAPI):
    with TestClient(app) as client:
        create_transaction(app)
        create_transaction(app)

        response = client.get(
            "/historic/1/2022-07-12T03:40:23.123Z/2022-07-14T03:40:23.123Z"
        )

        assert response.status_code == 200
        assert response.json() == {
            "transactions": [
                {
                    "client_id": 1,
                    "transaction_timestamp": "2022-07-13T03:40:23.123000",
                    "value": 10.17,
                    "description": "string",
                },
                {
                    "client_id": 1,
                    "transaction_timestamp": "2022-07-13T03:40:23.123000",
                    "value": 10.17,
                    "description": "string",
                },
            ]
        }


def test_get_historic_transactions_should_(app: FastAPI):
    with TestClient(app) as client:
        create_transaction(app)
        create_transaction(app)

        response = client.get(
            "/historic/5/2022-07-12T03:40:23.123Z/2022-07-15T03:40:23.123Z"
        )
        print(response.text)

        assert response.status_code == 200
        assert response.json() == {"transactions": []}
