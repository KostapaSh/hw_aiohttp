import asyncio
import configbd
from sqlalchemy import Integer, String, Column,  DateTime, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(configbd.db_link_asy, echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

class Advert(Base):

    __tablename__ = 'advertisements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    creation_date = Column(DateTime, server_default=func.now())
