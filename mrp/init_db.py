#!/usr/bin/env python3
"""Initialize MRP database tables from schema.sql"""
from pathlib import Path

import mysql.connector

from db import get_db_connection


def main():
    schema = Path(__file__).parent / "schema.sql"
    sql = schema.read_text(encoding="utf-8")
    lines = []
    for line in sql.splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        lines.append(line)
    clean_sql = "\n".join(lines)
    statements = [s.strip() for s in clean_sql.split(";") if s.strip()]

    conn = get_db_connection()
    cur = conn.cursor()
    for stmt in statements:
        try:
            cur.execute(stmt)
        except mysql.connector.Error as e:
            if e.errno not in (1050, 1062):
                print(f"Warning [{e.errno}]: {e}")
                print(f"  Statement: {stmt[:80]}...")
    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized successfully.")


if __name__ == "__main__":
    main()
