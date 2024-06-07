from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date, datetime
from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()



class Roll(Base):
    __tablename__ = 'rolls'
    id = Column(Integer, primary_key=True, index=True)
    length = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    date_added = Column(DateTime, default=datetime.utcnow)
    date_removed = Column(DateTime, nullable=True)


# Pydantic модели для запросов и ответов
class RollCreate(BaseModel):
    length: float = Field(..., gt=0, description="Длина рулона")
    weight: float = Field(..., gt=0, description="Вес рулона")


class RollUpdate(BaseModel):
    length: Optional[float] = Field(None, gt=0, description="Длина рулона")
    weight: Optional[float] = Field(None, gt=0, description="Вес рулона")
    date_removed: Optional[datetime] = Field(None, description="Дата удаления рулона")


class RollOut(BaseModel):
    id: int
    length: float
    weight: float
    date_added: datetime
    date_removed: Optional[datetime]
