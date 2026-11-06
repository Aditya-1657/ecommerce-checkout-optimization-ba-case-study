"""Loads the CSV into an in-memory SQLite database and runs every query in 02_funnel_analysis.sql.
Usage:  python sql/run_in_sqlite.py
"""
import re, sqlite3, pandas as pd

con = sqlite3.connect(":memory:")
pd.read_csv("data/checkout_sessions.csv").to_sql("checkout_sessions", con, index=False)
script = open("sql/02_funnel_analysis.sql", encoding="utf-8").read()
queries = [q.strip() for q in re.split(r";\s*\n", script) if "SELECT" in q]
for i, q in enumerate(queries, 1):
    title = next((l for l in q.splitlines() if l.startswith("-- Q")), f"-- Q{i}")
    print("\n" + title)
    print(pd.read_sql(q, con).to_string(index=False))
