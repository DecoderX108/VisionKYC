"""MySQL storage for eKYC records.

Connection settings come from environment variables (set automatically by
docker-compose):

    MYSQL_HOST      (default: localhost)
    MYSQL_PORT      (default: 3306)
    MYSQL_USER      (default: root)
    MYSQL_PASSWORD  (default: empty)
    MYSQL_DATABASE  (default: ekyc)

The `users` table is created automatically on first use.
"""
import os
import time
import logging
from contextlib import contextmanager

import mysql.connector
import pandas as pd

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id          VARCHAR(255) NOT NULL PRIMARY KEY,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Create Time',
    name        VARCHAR(255),
    father_name VARCHAR(255),
    dob         DATE,
    id_type     VARCHAR(255) NOT NULL,
    embedding   LONGTEXT
)
"""

_table_ready = False


def _db_config():
    return {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "ekyc"),
    }


def get_connection(retries=10, delay=3):
    """Open a new connection, retrying while the database is still starting."""
    cfg = _db_config()
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            return mysql.connector.connect(connection_timeout=10, **cfg)
        except mysql.connector.Error as e:
            last_err = e
            logging.warning(f"MySQL not ready ({attempt}/{retries}): {e}")
            time.sleep(delay)
    raise last_err


@contextmanager
def _connection():
    global _table_ready
    conn = get_connection()
    try:
        if not _table_ready:
            cur = conn.cursor()
            cur.execute(CREATE_TABLE_SQL)
            conn.commit()
            cur.close()
            _table_ready = True
        yield conn
    finally:
        conn.close()


def insert_records(text_info):
    sql = ("INSERT INTO users(id, name, father_name, dob, id_type, embedding) "
           "VALUES (%s, %s, %s, %s, %s, %s)")
    value = (
        text_info['ID'],
        text_info['Name'],
        text_info["Father's Name"],
        text_info['DOB'],  # 'YYYY-MM-DD'
        text_info['ID Type'],
        str(text_info['Embedding']),
    )
    with _connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, value)
        conn.commit()
        cur.close()


def fetch_records(text_info):
    sql = "SELECT * FROM users WHERE id = %s"
    with _connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, (text_info['ID'],))
        rows = cur.fetchall()
        cur.close()
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def check_duplicacy(text_info):
    return fetch_records(text_info).shape[0] > 0
