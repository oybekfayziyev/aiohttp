import jwt
import sqlalchemy
from config.setup import mysql_url
from sqlalchemy import create_engine
from aiohttp.web import HTTPBadRequest
from sqlalchemy.exc import SQLAlchemyError
from config.setup import JWT_ALGORITHM, JWT_SECRET


class CreateEngine:
    def __init__(self, url=mysql_url):
        self.url = url

    async def __aenter__(self):
        try:
            connectable = create_engine(mysql_url)
            self.connection = connectable.connect()
            return self.connection
        except sqlalchemy.exc.OperationalError as err:
            self.connection = None
            raise ValueError("Unable to connect database %s" % err)

    async def __aexit__(self, exc_type, exc, tb):
        if self.connection:
            self.connection.close()


def jwt_encrypt(payload):
    encoded = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded


def jwt_decrypt(token):
    try:
        decode = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
    except jwt.exceptions.InvalidSignatureError:
        raise HTTPBadRequest()
    return decode


def sql_raw_query():
    sql = """
        select test.coupons.user as user, test.users.username, test.users.name, test.users.surname, test.coupons.event as event_id, test.events.title as event_title, count(test.coupons.user) as event_count, (
            select count(tc.user)
            from test.coupons as tc
            where tc.user = test.coupons.user
        ) as total_events
        from test.coupons
        left join test.users on test.users.id = test.coupons.user
        left join test.events on test.events.id = test.coupons.event 
        group by test.coupons.user, test.coupons.event 
        having total_events >= 3
        """
    return sql


def sql_raw_events():
    sql = """
        SELECT test.events.title, test.users.username, test.users.name, coupons.hash, test.events.date
        FROM test.coupons as coupons
        left join test.events on test.events.id = coupons.event
        left join test.users on test.users.id = coupons.user    
    """
    return sql
