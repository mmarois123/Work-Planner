#!/usr/bin/env python3
"""Migrate local SQLite database to Turso cloud.

Reads from local Work-Planner/data/workplanner.db and writes all rows
to the Turso database specified by TURSO_DATABASE_URL / TURSO_AUTH_TOKEN.

Usage:
    # Load env vars from .env, then run:
    python migrate_to_turso.py
"""

import os
import sqlite3
import sys

# Load .env file
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip()

TURSO_URL = os.environ.get("TURSO_DATABASE_URL")
TURSO_TOKEN = os.environ.get("TURSO_AUTH_TOKEN")

if not TURSO_URL or not TURSO_TOKEN:
    print("ERROR: Set TURSO_DATABASE_URL and TURSO_AUTH_TOKEN in .env")
    sys.exit(1)

import libsql_client

# Connect to local SQLite
LOCAL_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "workplanner.db")
if not os.path.exists(LOCAL_DB):
    print(f"ERROR: Local database not found at {LOCAL_DB}")
    sys.exit(1)

local = sqlite3.connect(LOCAL_DB)
local.row_factory = sqlite3.Row

# Connect to Turso
# Convert libsql:// to https:// for HTTP transport (avoids WebSocket issues)
http_url = TURSO_URL.replace("libsql://", "https://")
print(f"Connecting to Turso: {http_url}")
remote = libsql_client.create_client_sync(url=http_url, auth_token=TURSO_TOKEN)

# Schema — create tables first
SCHEMA_STATEMENTS = [
    """CREATE TABLE IF NOT EXISTS areas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT NOT NULL UNIQUE,
        title TEXT NOT NULL, position INTEGER NOT NULL DEFAULT 0)""",
    """CREATE TABLE IF NOT EXISTS sections (
        id INTEGER PRIMARY KEY AUTOINCREMENT, area_id INTEGER NOT NULL REFERENCES areas(id),
        name TEXT NOT NULL, position INTEGER NOT NULL DEFAULT 0)""",
    """CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT, section_id INTEGER NOT NULL REFERENCES sections(id),
        title TEXT NOT NULL, description TEXT DEFAULT '', done INTEGER NOT NULL DEFAULT 0,
        priority INTEGER DEFAULT NULL, due_date TEXT DEFAULT NULL,
        delegated_to TEXT DEFAULT NULL, position INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        completed_at TEXT DEFAULT NULL, archived INTEGER NOT NULL DEFAULT 0)""",
    """CREATE TABLE IF NOT EXISTS subtasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT, task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
        title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0, position INTEGER NOT NULL DEFAULT 0)""",
    """CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE,
        color TEXT NOT NULL DEFAULT '#6b7280')""",
    """CREATE TABLE IF NOT EXISTS task_tags (
        task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
        tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
        PRIMARY KEY (task_id, tag_id))""",
    """CREATE TABLE IF NOT EXISTS recurrence_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL UNIQUE REFERENCES tasks(id) ON DELETE CASCADE,
        pattern TEXT NOT NULL, interval INTEGER NOT NULL DEFAULT 1,
        days_of_week TEXT DEFAULT NULL, next_due TEXT DEFAULT NULL)""",
]

print("Creating schema...")
for stmt in SCHEMA_STATEMENTS:
    remote.execute(stmt)
print("Schema created.")

# Migration order (respects foreign keys)
TABLES = ["areas", "sections", "tasks", "subtasks", "tags", "task_tags", "recurrence_rules"]

for table in TABLES:
    rows = local.execute(f"SELECT * FROM {table}").fetchall()
    if not rows:
        print(f"  {table}: 0 rows (skipped)")
        continue

    cols = rows[0].keys()
    placeholders = ", ".join(["?"] * len(cols))
    col_names = ", ".join(cols)
    insert_sql = f"INSERT OR IGNORE INTO {table} ({col_names}) VALUES ({placeholders})"

    count = 0
    for row in rows:
        vals = [row[c] for c in cols]
        try:
            remote.execute(insert_sql, vals)
            count += 1
        except Exception as e:
            print(f"  WARNING: {table} row failed: {e}")

    print(f"  {table}: {count} rows migrated")

# Verify
for table in TABLES:
    rs = remote.execute(f"SELECT COUNT(*) as c FROM {table}")
    count = rs.rows[0]["c"] if rs.rows else 0
    print(f"  {table}: {count} rows in Turso")

remote.close()
local.close()
print("\nMigration complete!")
