# IDE: PyCharm
# Project: scrap.test.task

import os
import datetime
import zipfile
from pathlib import Path

import pandas as pd
from sqlalchemy import String, Date, BigInteger, create_engine, text, URL
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


class Base(DeclarativeBase):
    pass


class RiaUsedCars(Base):
    __tablename__ = "ria_used_cars"
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(index=True, unique=True)  # url (строка)
    title: Mapped[str]  # title (строка)
    price_usd: Mapped[int]  # price_usd (число)
    odometer: Mapped[int]  # odometer (число, нужно перевести 95 тыс. в 95000 и записать как число)
    username: Mapped[str]  # username (строка)
    phone_number: Mapped[int] = mapped_column(BigInteger)  # phone_number (число, пример структуры: +38063……..) ? it does not fit into int32
    image_url: Mapped[str]  # image_url (строка)
    images_count: Mapped[int]  # images_count (число)
    car_number: Mapped[str] = mapped_column(String(30))  # car_number (строка)
    car_vin: Mapped[str] = mapped_column(String(30))  # car_vin (строка)
    datetime_found: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False, server_default=text('CURRENT_DATE'),
        default=datetime.date.today, onupdate=datetime.date.today,
    )  # datetime_found (дата сохранения в базу)

    def __str__(self) -> str:
        return f"{self.url}"


def booleanize(s: str) -> bool:
    return False if s.lower() in ('false', '0', '0.0', '', 'none') else True


DB_USER = os.getenv('DB_USER') or 'scrap_test_task_user'
DB_PASSWORD = os.getenv('DB_PASSWORD') or '12345678'
DB_HOST = os.getenv('DB_HOST') or 'localhost'
DB_PORT = int(os.getenv('DB_PORT')) or 5432
DB_NAME = os.getenv('DB_NAME') or 'scrap_test_task'
DB_ECHO = booleanize(os.getenv('DB_ECHO') or 'True')
DB_DROP_TABLE = booleanize(os.getenv('DB_DROP_TABLE') or 'False')
DUMPS_DIR = os.getenv('DUMPS_DIR') or './dumps'

if not Path(DUMPS_DIR).is_dir():
    Path(DUMPS_DIR).mkdir(parents=True, exist_ok=True)

engine = create_engine(
    URL.create(
        "postgresql+psycopg", username=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DB_NAME
    ),
    echo=DB_ECHO
)

if DB_DROP_TABLE:
    Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)


def update_or_insert(item_info: dict):
    with Session(engine) as session:
        url = item_info['url']
        try:
            car: RiaUsedCars = session.query(RiaUsedCars).filter(RiaUsedCars.url == url).with_for_update().one()
        except NoResultFound as exc:
            car = RiaUsedCars(**item_info)
            session.add(car)
        else:
            for n, v in item_info.items():
                if n not in (RiaUsedCars.url, RiaUsedCars.id):
                    setattr(car, n, v)

        session.commit()


def dump(file):
    table_name = RiaUsedCars.__tablename__
    with engine.connect() as conn, conn.begin():
        data = pd.read_sql_table(table_name, conn)
        csv = data.to_csv(index=False)
        with zipfile.ZipFile(file, 'a') as _zip:
            _zip.writestr(f'{table_name}-{datetime.datetime.now()}.csv', csv)
