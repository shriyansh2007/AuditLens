
import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = "data/auditlens.db"

def initialize_database():
    Path("data").mkdir(exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS investigations (
                transaction_id TEXT PRIMARY KEY,
                status TEXT DEFAULT 'Open',
                notes TEXT DEFAULT ''
            )
        """)

def save_audit_data(risk_results, findings):
    initialize_database()

    with sqlite3.connect(DB_PATH) as conn:
        risk_results.to_sql("transactions", conn, if_exists="replace", index=False)
        findings.to_sql("findings", conn, if_exists="replace", index=False)

        conn.execute("""
            INSERT OR IGNORE INTO investigations (transaction_id)
            SELECT transaction_id FROM transactions WHERE risk_score > 0
        """)

def load_data(query):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn)

def update_investigation(transaction_id, status, notes):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO investigations (transaction_id, status, notes)
            VALUES (?, ?, ?)
            ON CONFLICT(transaction_id)
            DO UPDATE SET status=excluded.status, notes=excluded.notes
        """, (transaction_id, status, notes))
