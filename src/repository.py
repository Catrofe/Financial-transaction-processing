import logging
from decimal import Decimal
from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.exc import DataError, IntegrityError, OperationalError, StatementError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

from src.database import Transaction
from src.models import (
    GetVolumeFinancialInput,
    HistoricOutput,
    TransactionId,
    TransactionInput,
    Transactions,
)

logger = logging.getLogger()

Base = declarative_base()


class TransactionRepository:
    def __init__(self, db_url: str) -> None:
        self.engine = create_async_engine(
            db_url,
            echo=False,
        )
        self.Session = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    async def create_transaction(
        self, new_request: TransactionInput
    ) -> Optional[TransactionId]:
        transaction = Transaction(
            client_id=new_request.client_id,
            transaction_timestamp=new_request.transaction_timestamp,
            value=int(new_request.value),
            description=new_request.description,
        )
        try:
            async with self.Session() as session:
                session.add(transaction)
                await session.commit()

                logger.info(f"Created a new transaction with id: {transaction.id}")
                return transaction.id

        except (DataError, IntegrityError, OperationalError, StatementError):
            logger.exception("Failed to create transaction")
            await session.rollback()
            raise

    async def get_balance_client(self, client_id: int) -> Optional[Decimal]:
        try:
            async with self.Session() as session:
                query_select = await session.execute(
                    select(func.sum(Transaction.value)).where(
                        Transaction.client_id == client_id
                    )
                )
                balance = query_select.scalar()

                if not balance:
                    return None

                return Decimal(balance / 100)

        except (DataError, IntegrityError, OperationalError, StatementError):
            logger.exception("Failed to get balance")
            await session.rollback()
            raise

    async def get_financial_volume(
        self, request: GetVolumeFinancialInput
    ) -> Optional[Decimal]:
        try:
            async with self.Session() as session:
                query_select = await session.execute(
                    select(func.sum(Transaction.value)).where(
                        and_(
                            Transaction.client_id == request.client_id,
                            Transaction.transaction_timestamp >= request.date_initial,
                            Transaction.transaction_timestamp <= request.date_end,
                        )
                    )
                )
                balance = query_select.scalar()

                if not balance:
                    return None

            return Decimal(balance / 100)

        except (DataError, IntegrityError, OperationalError, StatementError):
            logger.exception("Failed to get balance")
            await session.rollback()
            raise

    async def get_historic_client(
        self, request: GetVolumeFinancialInput
    ) -> HistoricOutput:
        try:
            async with self.Session() as session:
                query_select = await session.execute(
                    select((Transaction)).where(
                        and_(
                            Transaction.client_id == request.client_id,
                            Transaction.transaction_timestamp >= request.date_initial,
                            Transaction.transaction_timestamp <= request.date_end,
                        )
                    )
                )
                balance = query_select.scalars()

                historic = []
                for item in balance:
                    historic.append(
                        Transactions(
                            client_id=item.client_id,
                            transaction_timestamp=item.transaction_timestamp,
                            value=Decimal(
                                str(item.value)[:-2] + "." + str(item.value)[-2:]
                            ),
                            description=item.description,
                        )
                    )

                return HistoricOutput(transactions=historic)

        except (DataError, IntegrityError, OperationalError, StatementError):
            logger.exception("Failed to get balance")
            await session.rollback()
            raise
