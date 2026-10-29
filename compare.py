import sqlite3

conn = sqlite3.connect("evals.db")
rows = conn.execute(
    "SELECT id, name, created_at, passed, total, avg_score FROM runs ORDER BY id"
).fetchall()

if not rows:
    print("No runs yet. Run run_cases.py first.")
else:
    print(f"{'id':<3} {'name':<20} {'when':<20} {'passed':<8} {'avg':<5}")
    print("-" * 60)
    for r in rows:
        print(f"{r[0]:<3} {r[1]:<20} {r[2]:<20} {r[3]}/{r[4]:<6} {r[5]:.1f}")