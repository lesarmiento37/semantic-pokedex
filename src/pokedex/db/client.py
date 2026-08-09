from __future__ import annotations

import json
import os
from contextlib import contextmanager
from typing import Generator

import boto3
import psycopg


@contextmanager
def get_connection() -> Generator[psycopg.Connection, None, None]:
    secret_arn = os.getenv("DB_SECRET_ARN")
    if not secret_arn:
        raise RuntimeError("DB_SECRET_ARN is required")

    secrets = boto3.client("secretsmanager")
    secret_payload = secrets.get_secret_value(SecretId=secret_arn)
    secret_dict = json.loads(secret_payload.get("SecretString", "{}"))

    host = secret_dict.get("host") or os.getenv("DB_HOST")
    port = int(secret_dict.get("port") or os.getenv("DB_PORT", "5432"))
    dbname = secret_dict.get("dbname") or os.getenv("DB_NAME", "semantic_pokedex")
    user = secret_dict.get("username") or secret_dict.get("user")
    password = secret_dict.get("password")

    if not all([host, dbname, user, password]):
        raise RuntimeError("Database connection fields are missing in secret/env configuration")

    kwargs = {
        "host": host,
        "port": port,
        "dbname": dbname,
        "user": user,
        "autocommit": False,
    }
    kwargs["password"] = password
    conn = psycopg.connect(**kwargs)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
