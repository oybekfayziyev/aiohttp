import logging

from aiohttp import web

from app.middlewares import jwt_custom_middleware

from config.setup import mysql_url, WHITE_LIST, JWT_SECRET, JWT_ALGORITHM


def setup_config(application):
    application["database"] = mysql_url


def setup_routes(application):
    from config.urls import path

    path(application)


def setup_app(application):
    setup_config(application)
    setup_routes(application)


app = web.Application(
    middlewares=[
        jwt_custom_middleware(
            secret_or_pub_key=JWT_SECRET, whitelist=WHITE_LIST, algorithms=JWT_ALGORITHM
        ),
    ]
)
logging.basicConfig(level=logging.DEBUG)


if __name__ == "__main__":

    setup_app(app)
    web.run_app(app)
