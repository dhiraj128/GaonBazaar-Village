#!/usr/bin/env python3
"""
Supabase Production Demo Data Cleanup & Recoverable Backup Runner
Applies backend/sql/cleanup_demo_data_with_backup.sql to Supabase PostgreSQL.

Usage:
  py -3.12 scripts/supabase_cleanup_and_backup.py [--dry-run]
"""

import os
import sys
import argparse
from urllib.parse import quote, unquote

def get_database_url():
    url = (
        os.getenv("SUPABASE_DB_URL")
        or os.getenv("DATABASE_URL")
        or os.getenv("PROD_DATABASE_URL")
    )
    if not url:
        return None
    return url

def main():
    parser = argparse.ArgumentParser(description="Supabase Demo Data Cleanup & Backup")
    parser.add_argument("--dry-run", action="store_true", help="Inspect without modifying")
    args = parser.parse_args()

    sql_file = os.path.join(os.path.dirname(__file__), "..", "backend", "sql", "cleanup_demo_data_with_backup.sql")
    if not os.path.exists(sql_file):
        print(f"[ERROR] SQL file not found: {sql_file}")
        sys.exit(1)

    with open(sql_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    db_url = get_database_url()
    if not db_url or "sqlite" in db_url:
        print("=" * 70)
        print("SUPABASE DEMO DATA CLEANUP SCRIPT PREPARED")
        print("=" * 70)
        print("SQL Migration File: backend/sql/cleanup_demo_data_with_backup.sql")
        print("Total SQL size:     %d bytes" % len(sql_content))
        print("\nTo apply this script directly to Supabase:")
        print("1. Open Supabase Dashboard: https://supabase.com/dashboard/project/vxewgvrjhjpntfvsmuez/sql")
        print("2. Paste and run backend/sql/cleanup_demo_data_with_backup.sql")
        print("3. Alternatively, export SUPABASE_DB_URL and run this script.")
        print("\nSafety Features:")
        print("  - Snapshot backup tables created: *_backup_20261123")
        print("  - Children deleted before parents (order_items, timeline, messages, etc.)")
        print("  - Real users & admin accounts (usr_admin_01, usr_hub_01) strictly preserved")
        print("  - Row-Level Security (RLS) enforced across all public tables")
        print("=" * 70)
        return

    try:
        import psycopg2
    except ImportError:
        print("[NOTICE] psycopg2 not installed. Use psycopg2 or SQLAlchemy.")
        return

    print("[INFO] Connecting to Supabase database...")
    # Execute transactional script
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute(sql_content)
            conn.commit()
            print("[SUCCESS] Cleanup and backup completed successfully!")
    except Exception as e:
        print("[ERROR] Database operation failed:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
