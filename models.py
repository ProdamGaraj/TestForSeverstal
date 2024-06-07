from typing import List, Optional
from pydantic import Field,BaseModel
from datetime import date, datetime
from sqlalchemy import Column, Integer, Float, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Roll(Base):
    __tablename__ = 'rolls'
    id = Column(Integer, primary_key=True, index=True)
    length = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    date_added = Column(Date, default=date.today())
    date_removed = Column(Date, nullable=True)


# Pydantic модели для запросов и ответов
class RollCreate(BaseModel):
    length: float = Field(..., gt=0, description="Длина рулона")
    weight: float = Field(..., gt=0, description="Вес рулона")


class RollUpdate(BaseModel):
    length: Optional[float] = Field(None, gt=0, description="Длина рулона")
    weight: Optional[float] = Field(None, gt=0, description="Вес рулона")
    date_removed: Optional[date] = Field(None, description="Дата удаления рулона")


class RollOut(BaseModel):
    id: int
    length: float
    weight: float
    date_added: date
    date_removed: Optional[date]
