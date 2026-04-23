import sqlite3
import csv
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "vocalizations.db"
OUT_PATH = Path(__file__).parent.parent.parent / "data" / "exports" / "vocalizations.csv"

con = sqlite3.connect(DB_PATH)
cur = con.execute("SELECT * FROM vocalizations")
rows = cur.fetchall()
headers = [d[0] for d in cur.description]
con.close()

with open(OUT_PATH, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(rows)

print(f"Exported {len(rows)} rows to {OUT_PATH}")
