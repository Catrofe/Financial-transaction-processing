from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


async def setup_db(db_url: str) -> None:
    engine = create_async_engine(
        db_url,
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, nullable=True)
    transaction_timestamp = Column(DateTime, nullable=True)
    value = Column(Integer, nullable=True)
    description = Column(String, nullable=True)
