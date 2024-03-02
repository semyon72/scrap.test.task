# IDE: PyCharm
# Project: scrap.test.task
import functools
import os
import datetime
import zipfile
from pathlib import Path
from subprocess import Popen, PIPE

from environs import Env
from sqlalchemy import String, Date, BigInteger, create_engine, text, URL, Engine
from sqlalchemy.exc import NoResultFound, OperationalError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

from app.helpers.env import prefixed_env_to_dict


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


class DBUtils:
    env_db_config_prfx = 'DB_CONFIG'
    env_db_option_prfx = 'DB_OPTION'

    env_db_settings = {
        env_db_config_prfx: ['USERNAME', 'PASSWORD', 'HOST', 'PORT', 'DATABASE'],
        env_db_option_prfx: [('ECHO', Env.bool), ('DROP_TABLE', Env.bool), 'DUMPS_DIR']
    }
    default_dumps_dir = './dumps'

    def __init__(self, env: Env):
        self.env = env

    @functools.cached_property
    def engine(self):
        engine = self.check_db()
        db_opts = self._prefixed_env_to_dict(self.env_db_option_prfx)
        if db_opts.get('drop_table', False):
            Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        return engine

    @functools.lru_cache
    def _prefixed_env_to_dict(self, env_db_setting: str = None):
        env_db_setting = env_db_setting or next(iter(self.env_db_settings.keys()))
        res = prefixed_env_to_dict(self.env, env_db_setting, self.env_db_settings[env_db_setting])
        return res

    def check_db(self) -> Engine:
        user_cred = self._prefixed_env_to_dict(self.env_db_config_prfx)
        pg_cred = user_cred | {
            'database': self.env('POSTGRES_DB', 'postgres'),
            'username': self.env('POSTGRES_USER', 'postgres'),
            'password': self.env('POSTGRES_PASSWORD', ''),
        }
        db_opts = self._prefixed_env_to_dict(self.env_db_option_prfx)
        echo = db_opts.get('echo', True)

        pg_url = URL.create("postgresql+psycopg", **pg_cred)
        engine = create_engine(pg_url, echo=echo)
        try:
            con = engine.connect()
        except OperationalError as exc:
            # bad connection for default postgres credentials
            # psycopg.OperationalError: connection failed: FATAL:  password authentication failed for user "postgres"
            raise
        else:
            # if used default user - nothing to check
            usr_url = URL.create("postgresql+psycopg", **user_cred)
            if pg_url == usr_url:
                return engine

            # set isolation_level="AUTOCOMMIT"
            con.execution_options(isolation_level='AUTOCOMMIT')

            # test database existing
            sql = "SELECT datname FROM pg_catalog.pg_database WHERE lower(datname) = lower(:database);"
            result = con.execute(text(sql), {'database': user_cred['database']})
            if result.one_or_none() is None:
                # check user
                sql = "SELECT usename FROM pg_catalog.pg_user WHERE lower(usename) = lower(:username);"
                result = con.execute(text(sql), {'username': user_cred['username']})
                if result.one_or_none() is None:
                    # user does not exist
                    con.execute(text(f"CREATE USER {user_cred['username']} PASSWORD '{user_cred['password']}'"))

                con.execute(text(f'CREATE DATABASE {user_cred["database"]} WITH OWNER={user_cred["username"]}'))
        finally:
            engine.dispose()

        return create_engine(usr_url, echo=echo)

    def update_or_insert(self, item_info: dict):
        with Session(self.engine) as session:
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

    @functools.cached_property
    def dump_path(self) -> Path:
        db_opts = self._prefixed_env_to_dict(self.env_db_option_prfx)
        dump_path = Path(db_opts.get('dumps_dir', self.default_dumps_dir))
        if not dump_path.is_dir():
            dump_path.mkdir(parents=True, exist_ok=True)

        return dump_path

    def _dump_export(self, popen_args: list, zip_name: str, file_name: str):
        usr_db_conf = self._prefixed_env_to_dict(self.env_db_config_prfx)
        env = os.environ | {
            'PGPASSWORD': usr_db_conf['password'],
            'PGDATABASE': usr_db_conf['database'],
            'PGHOST': usr_db_conf['host'],
            'PGPORT': usr_db_conf['port'],
            'PGUSER': usr_db_conf['username']
        }
        with Popen(popen_args, stdout=PIPE, env=env) as proc:
            with zipfile.ZipFile(zip_name, 'a') as _zip:
                _zip.writestr(file_name, proc.stdout.read())

    def dump(self, zip_name: str = None):
        if not zip_name:
            zip_name = f'{str(self.dump_path)}/dump-{datetime.date.today()}.zip'

        table_name = RiaUsedCars.__tablename__
        self._dump_export(
            ["pg_dump", "-t", f"{table_name}"], zip_name, f'{table_name}-{datetime.datetime.now()}.sql'
        )

    def to_csv(self, zip_name: str = None):
        if not zip_name:
            zip_name = f'{str(self.dump_path)}/export-{datetime.date.today()}.zip'

        table_name = RiaUsedCars.__tablename__
        cmd = f"copy {table_name} TO STDOUT DELIMITER ',' CSV ENCODING 'UTF8' QUOTE '\"' ESCAPE '''' HEADER;"
        self._dump_export(["psql", "-c", cmd], zip_name, f'{table_name}-{datetime.datetime.now()}.csv')
