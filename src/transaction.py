import logging

from src.models import (
    Error,
    GetBalanceOutput,
    GetVolumeFinancialInput,
    HistoricOutput,
    TransactionInput,
    TransactionOutput,
)
from src.repository import TransactionRepository

logger = logging.getLogger()


async def create_transaction(
    request: TransactionInput, repository: TransactionRepository
) -> TransactionOutput | Error:
    try:
        value: str = str(request.value)
        if "." not in str(value):
            value = str(value) + "00"
        elif request.value < 0:
            return Error(
                reason="BAD_REQUEST", message="VALUE_MUST_BE_POSITIVE", status_code=400
            )

        request.value = int(str(value).replace(".", ""))

        id = await repository.create_transaction(request)

        return TransactionOutput(transaction_id=id, message="TRANSACTION_CREATED")

    except Exception as exc:
        logger.exception("Error while creating transaction")
        return Error(reason="UNKNOWN", message=repr(exc), status_code=500)


async def get_balance_client(
    client_id: int, repository: TransactionRepository
) -> GetBalanceOutput | Error:
    try:
        get_repository = await repository.get_balance_client(client_id)

        if get_repository is None:
            return Error(
                reason="BAD_REQUEST",
                message="NO_VALUE_FOUND_FOR_THESE_PARAMETERS",
                status_code=404,
            )

        return GetBalanceOutput(balance=get_repository)
    except Exception as exc:
        logger.exception("Error while creating transaction")
        return Error(reason="UNKNOWN", message=repr(exc), status_code=500)


async def get_financial_volume(
    request: GetVolumeFinancialInput, repository: TransactionRepository
) -> GetBalanceOutput | Error:
    try:
        get_repository = await repository.get_financial_volume(request)

        if get_repository is None:
            return Error(
                reason="BAD_REQUEST",
                message="NO_VALUE_FOUND_FOR_THESE_PARAMETERS",
                status_code=404,
            )

        return GetBalanceOutput(balance=get_repository)

    except Exception as exc:
        logger.exception("Error while get financial volume")
        return Error(reason="UNKNOWN", message=repr(exc), status_code=500)


async def get_historic_client(
    request: GetVolumeFinancialInput, repository: TransactionRepository
) -> HistoricOutput | Error:
    try:
        return await repository.get_historic_client(request)

    except Exception as exc:
        logger.exception("Error while get financial volume")
        return Error(reason="UNKNOWN", message=repr(exc), status_code=500)
