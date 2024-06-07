import http

from sqlalchemy.exc import NoResultFound, IntegrityError, SQLAlchemyError

from models import *
from fastapi import FastAPI, HTTPException, Query, Path, Body
from typing import List, Optional

from fastapi_sqlalchemy import DBSessionMiddleware, db
from pydantic import BaseModel, Field
from datetime import date, datetime
from sqlalchemy import create_engine, Column, Integer, Float, DateTime, func, between, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import logging
import os
from dotenv import load_dotenv

load_dotenv('.env')

app = FastAPI()
# to avoid csrftokenError
app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])
# logging.basicConfig(filename=os.environ['LOG_FILE'],
#                     level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# Create a logger
logger = logging.getLogger('alembic')
logger.setLevel(logging.DEBUG)

# Create a file handler to redirect log output to a file
file_handler = logging.FileHandler(os.environ['LOG_FILE'])
file_handler.setLevel(logging.INFO)

# Create a formatter and add it to the file handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

status_codes = http.HTTPStatus


def handle_db_error(err: Exception) -> HTTPException:
    if isinstance(err, NoResultFound):
        return HTTPException(status_code=404, detail="Resource not found")
    elif isinstance(err, IntegrityError):
        return HTTPException(status_code=400, detail="Integrity error")
    else:
        return HTTPException(status_code=500, detail="Database error")


# Эндпоинты API
@app.post("/rolls/", response_model=RollOut)
def create_roll(roll: RollCreate):
    try:
        db_roll = Roll(**roll.model_dump())
        db.session.add(db_roll)
        db.session.commit()
        db.session.refresh(db_roll)
        return db_roll
    except SQLAlchemyError as err:
        db.session.rollback()
        raise handle_db_error(err)


@app.get("/rolls/", response_model=List[RollOut])
def read_rolls(
        id: Optional[int] = Query(None),
        weight_min: Optional[float] = Query(None),
        weight_max: Optional[float] = Query(None),
        length_min: Optional[float] = Query(None),
        length_max: Optional[float] = Query(None),
        date_added_start: Optional[date] = Query(None),
        date_added_end: Optional[date] = Query(None),
        date_removed_start: Optional[date] = Query(None),
        date_removed_end: Optional[date] = Query(None)
):
    try:
        query = db.session.query(Roll)
        if id:
            query = query.filter(Roll.id == id)
        if weight_min is not None and weight_max is not None:
            query = query.filter(between(Roll.weight, weight_min, weight_max))
        if length_min is not None and length_max is not None:
            query = query.filter(between(Roll.length, length_min, length_max))
        if date_added_start and date_added_end:
            query = query.filter(between(Roll.date_added, date_added_start, date_added_end))
        if date_removed_start and date_removed_end:
            query = query.filter(
                or_(Roll.date_removed is None, between(Roll.date_removed, date_removed_start, date_removed_end)))

        rolls = query.all()
        return rolls
    except SQLAlchemyError as err:
        db.session.rollback()
        raise handle_db_error(err)


@app.get("/rolls/{roll_id}", response_model=RollOut)
def read_roll(roll_id: int):
    try:
        roll = db.session.query(Roll).filter(Roll.id == roll_id).first()
        if roll is None:
            raise HTTPException(status_code=404, detail="Roll not found")
        return roll
    except SQLAlchemyError as err:
        db.session.rollback()
        raise handle_db_error(err)


@app.put("/rolls/{roll_id}", response_model=RollOut)
def update_roll(roll_id: int, roll: RollUpdate):
    try:
        db_roll = db.session.query(Roll).filter(Roll.id == roll_id).first()
        if db_roll is None:
            raise HTTPException(status_code=404, detail="Roll not found")
        for var, value in vars(roll).items():
            setattr(db_roll, var, value) if value else None
        db.session.commit()
        db.session.refresh(db_roll)
        return db_roll
    except SQLAlchemyError as err:
        db.session.rollback()
        raise handle_db_error(err)


@app.delete("/rolls/{roll_id}", response_model=RollOut)
def delete_roll(roll_id: int):
    try:
        db_roll = db.session.query(Roll).filter(Roll.id == roll_id).first()
        if db_roll is None:
            raise HTTPException(status_code=404, detail="Roll not found")
        db.session.delete(db_roll)
        db.session.commit()
        return db_roll
    except SQLAlchemyError as err:
        db.session.rollback()
        raise handle_db_error(err)


@app.get("/rolls/statistics/", response_model=RollOut)
def get_statistics(start_date: date, end_date: date):
    try:
        stats = db.session.query(
            func.count(Roll.id).label("total_rolls"),
            func.avg(Roll.length).label("average_length"),
            func.avg(Roll.weight).label("average_weight"),
            func.max(Roll.length).label("max_length"),
            func.min(Roll.length).label("min_length"),
            func.max(Roll.weight).label("max_weight"),
            func.min(Roll.weight).label("min_weight"),
        ).filter(
            Roll.date_added >= start_date,
            Roll.date_added <= end_date
        ).first()
        return stats
    except SQLAlchemyError as err:
        db.session.rollback()
        raise handle_db_error(err)
