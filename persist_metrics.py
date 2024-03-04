import sqlite3
import os
import json
from datetime import datetime, timedelta

os.chdir(os.path.dirname(__file__))

with open('config.json') as f:
    config = json.load(f)


def _create_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn


def _create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS systemdrip (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT,
            state TEXT,
            memory_current_mb REAL,
            cpu_usage_seconds REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')


def _insert_data(conn, service, state, memory_current_mb, cpu_usage_seconds):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO systemdrip (service, state, memory_current_mb, cpu_usage_seconds)
        VALUES (?, ?, ?, ?)
    ''', (service, state, memory_current_mb, cpu_usage_seconds))


def _delete_old_data(conn):
    cursor = conn.cursor()
    six_months_ago = datetime.now() - timedelta(days=int(config['persist_metrics_days']))
    cursor.execute('''
        DELETE FROM systemdrip
        WHERE timestamp < ?
    ''', (six_months_ago,))


def persist_metrics(service, state, memory_current_mb, cpu_usage_seconds):
    database = "systemdrip.db"
    conn = _create_connection(database)
    with conn:
        _create_table(conn)
        _insert_data(conn, service, state, memory_current_mb, cpu_usage_seconds)
        _delete_old_data(conn)
        conn.commit()
