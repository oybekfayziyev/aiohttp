import json
import aiohttp
import sqlalchemy
from uuid import uuid4
from sqlalchemy import orm
import sqlalchemy as alchemy
from datetime import datetime

from sqlalchemy.orm import Session

from sqlalchemy.sql import text
from .utils import CreateEngine, sql_raw_query, sql_raw_events
from aiohttp.web import json_response
from passlib.hash import pbkdf2_sha256
from config.setup import PASSWORD_HASHING
from sqlalchemy.exc import SQLAlchemyError

metadata = alchemy.MetaData()
Base = orm.declarative_base(metadata=metadata)


class User(Base):
    __tablename__ = "users"

    id = alchemy.Column(alchemy.Integer, primary_key=True)
    username = alchemy.Column(alchemy.String(255), unique=True)
    name = alchemy.Column(alchemy.String(128))
    surname = alchemy.Column(alchemy.String(128), nullable=True)
    token = alchemy.Column(alchemy.String(256))
    password = alchemy.Column(alchemy.String(256))
    timestamp = alchemy.Column(alchemy.DateTime(), default=datetime.now)

    @staticmethod
    def make_password(password):

        key = pbkdf2_sha256.encrypt(
            password,
            rounds=PASSWORD_HASHING["ITERATION"],
            salt_size=PASSWORD_HASHING["SALT"],
        )
        return key

    @staticmethod
    def check_password(password, hash_pass):
        return pbkdf2_sha256.verify(password, hash_pass)

    @staticmethod
    async def create_user(data: dict):

        async with CreateEngine() as conn:
            query = alchemy.select(alchemy.sql.expression.func.count()).where(
                User.username == data["username"]
            )
            user = conn.execute(query).fetchone()
            if user[0] > 0:
                raise aiohttp.web.HTTPBadRequest()

            query = User.__table__.insert().values(data)
            conn.execute(query)
            query = alchemy.select(User).where(User.username == data["username"])
            user = list(map(lambda x: dict(x), conn.execute(query)))

        return user

    @staticmethod
    async def get_user_by_id(user_id: int):
        async with CreateEngine() as conn:
            query = alchemy.select(User).where(User.id == user_id)
            query = list(map(lambda x: dict(x), conn.execute(query)))
            if not query:
                raise aiohttp.web.HTTPNotFound
            query = query[0]
            query["timestamp"] = str(query["timestamp"])
        return query

    @staticmethod
    async def get_user_by_username(username: str):

        async with CreateEngine() as conn:
            query = alchemy.select(alchemy.sql.expression.func.count()).where(
                User.username == username
            )
            user = conn.execute(query).fetchone()
            if user[0] == 0:
                raise aiohttp.web.HTTPNotFound()

            query = alchemy.select(User).where(User.username == username)
            user = list(map(lambda x: dict(x), conn.execute(query)))
        return user[0]

    async def get_user_events(self, user_id: int):

        async with CreateEngine() as conn:
            query = alchemy.select([User, Event]).where()


class Event(Base):

    __tablename__ = "events"

    id = alchemy.Column(alchemy.Integer, primary_key=True)
    title = alchemy.Column(alchemy.String(128))
    description = alchemy.Column(alchemy.Text(1024))
    price = alchemy.Column(alchemy.Float)
    remain = alchemy.Column(alchemy.Integer)
    date = alchemy.Column(alchemy.DateTime())
    timestamp = alchemy.Column(alchemy.DateTime(), default=datetime.now)

    async def create_event(self, data: dict):
        async with CreateEngine() as conn:
            query = Event.__table__.insert().values(**data)
            session = Session(conn)
            trans = session.begin()
            try:
                result = session.execute(query)
                event_id = result.lastrowid
                trans.commit()
            except SQLAlchemyError as e:
                trans.rollback()
                raise e
            event = await self.get_event_by_id(event_id)
        return event

    @staticmethod
    async def get_event_by_id(event_id: int):
        async with CreateEngine() as conn:
            query = alchemy.select(Event).where(Event.id == event_id)
            query = list(map(lambda x: dict(x), conn.execute(query)))
            if not query:
                raise aiohttp.web.HTTPNotFound
            query = query[0]
            query["date"] = str(query["date"])
            query["timestamp"] = str(query["timestamp"])

        return query

    @staticmethod
    async def get_events():
        async with CreateEngine() as conn:

            query = alchemy.select(Event).where(Event.remain > 0)
            events = list(map(lambda x: dict(x), conn.execute(query)))
            for event in events:
                event["date"] = str(event["date"])
                event["timestamp"] = str(event["timestamp"])
        return events

    @staticmethod
    async def update_event(event_id: int):
        async with CreateEngine() as conn:
            query = (
                Event.__table__.update()
                .where(Event.id == event_id, Event.remain > 0)
                .values(remain=Event.remain - 1)
            )
            conn.execute(query)


class Coupon(Base):

    __tablename__ = "coupons"

    id = alchemy.Column(alchemy.Integer, primary_key=True)
    user = alchemy.Column(alchemy.Integer, alchemy.ForeignKey("users.id"))
    event = alchemy.Column(alchemy.Integer, alchemy.ForeignKey("events.id"))
    hash = alchemy.Column(alchemy.String(128))
    timestamp = alchemy.Column(alchemy.DateTime(), default=datetime.now)

    @staticmethod
    async def get_coupon_by_id(coupon_id: int):
        async with CreateEngine() as conn:
            query = Coupon.__table__.select().where(Coupon.id == coupon_id)
            query = list(map(lambda x: dict(x), conn.execute(query)))
            if not query:
                raise aiohttp.web.HTTPNotFound
            query = query[0]
            query["timestamp"] = str(query["timestamp"])

        return query

    async def create_coupon(self, user_id, event_id):
        async with CreateEngine() as conn:
            await User.get_user_by_id(user_id)
            event = await Event.get_event_by_id(event_id)
            if not event["remain"]:
                raise aiohttp.web.HTTPBadRequest()

            await Event.update_event(event_id)
            coupon_hash = uuid4()
            query = Coupon.__table__.insert().values(
                user=user_id, event=event_id, hash=coupon_hash
            )
            session = Session(conn)
            trans = session.begin()
            try:
                result = session.execute(query)
                coupon_id = result.lastrowid
                trans.commit()
            except SQLAlchemyError as e:
                trans.rollback()
                raise e
            coupon = await self.get_coupon_by_id(coupon_id)
        return coupon

    @staticmethod
    async def get_users_coupons():
        async with CreateEngine() as conn:
            query = sql_raw_query()
            result = conn.execute(text(query)).mappings().all()

        return result

    @staticmethod
    async def get_events_list():
        async with CreateEngine() as conn:
            query = sql_raw_events()
            result = conn.execute(text(query)).mappings().all()

        return result
