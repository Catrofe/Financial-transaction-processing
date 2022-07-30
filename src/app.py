from dataclasses import dataclass
from datetime import datetime

from fastapi import FastAPI, HTTPException

from src.database import setup_db
from src.models import (
    Error,
    GetBalanceOutput,
    GetVolumeFinancialInput,
    HistoricOutput,
    TransactionInput,
    TransactionOutput,
)
from src.repository import TransactionRepository
from src.settings import Settings
from src.transaction import (
    create_transaction,
    get_balance_client,
    get_financial_volume,
    get_historic_client,
)


def create_app(settings: Settings = Settings()) -> FastAPI:
    app = FastAPI()

    @dataclass
    class ServerContext:
        repository: TransactionRepository

    context = ServerContext(repository=TransactionRepository(settings.db_url))

    @app.on_event("startup")
    async def startup_event() -> None:
        await setup_db(str(settings.db_url))

    @app.post("/transaction", status_code=201, response_model=TransactionOutput)
    async def register_transaction(request: TransactionInput) -> TransactionOutput:
        response = await create_transaction(request, context.repository)

        if isinstance(response, TransactionOutput):
            return response

        if isinstance(response, Error):
            raise HTTPException(response.status_code, response.message)

    @app.get("/transaction/{id}", status_code=200, response_model=GetBalanceOutput)
    async def get_balance(id: int) -> GetBalanceOutput:
        response = await get_balance_client(id, context.repository)

        if isinstance(response, GetBalanceOutput):
            return response

        if isinstance(response, Error):
            raise HTTPException(response.status_code, response.message)

    @app.get(
        "/transaction/{id}/{date_initial}/{date_end}",
        status_code=200,
        response_model=GetBalanceOutput,
    )
    async def get_volume_financial(
        id: int, date_initial: datetime, date_end: datetime
    ) -> GetBalanceOutput:

        request = GetVolumeFinancialInput(
            client_id=id, date_initial=date_initial, date_end=date_end
        )

        response = await get_financial_volume(request, context.repository)

        if isinstance(response, GetBalanceOutput):
            return response

        if isinstance(response, Error):
            raise HTTPException(response.status_code, response.message)

    @app.get(
        "/historic/{id}/{date_initial}/{date_end}",
        status_code=200,
        response_model=HistoricOutput,
    )
    async def get_historic(
        id: int, date_initial: datetime, date_end: datetime
    ) -> HistoricOutput:

        request = GetVolumeFinancialInput(
            client_id=id, date_initial=date_initial, date_end=date_end
        )

        response = await get_historic_client(request, context.repository)

        if isinstance(response, HistoricOutput):
            return response

        if isinstance(response, Error):
            raise HTTPException(response.status_code, response.message)

    return app
