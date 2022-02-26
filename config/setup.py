import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

SECRET_KEY = os.environ.get(
    "SECRET_KEY", "we+qv90$zu5p9-miffm@wg2%89ao#(%=6kro6wkv%)v%37x%si"
)

WHITE_LIST = (
    "/api/v1/account/create",
    "/api/v1/account/me",
)

DATABASE = {
    "NAME": os.environ.get("MYSQL_DATABASE", "test"),
    "USER": os.environ.get("MYSQL_USER", "root"),
    "PASSWORD": os.environ.get("MYSQL_PASSWORD", "qwerty123"),
    "HOST": os.environ.get("MYSQL_HOST", "localhost"),
    "PORT": os.environ.get("MYSQL_PORT", 3306),
}

mysql_url = f'mysql+mysqldb://{DATABASE["USER"]}:{DATABASE["PASSWORD"]}@{DATABASE["HOST"]}/{DATABASE["NAME"]}'


PASSWORD_HASHING = {
    "PASSWORD_HASH_ALGORITHM": "pbkdf2_sha256",
    "SALT": 32,
    "ITERATION": 100000,
}

JWT_SECRET = SECRET_KEY
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 36000
