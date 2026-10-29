"""FastAPI backend for the eval tool."""
import sqlite3
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

load_dotenv()

import run_engine  # noqa: E402  (the eval logic)

DB = "evals.db"
app = FastAPI(title="EvalKit")


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, created_at TEXT,
        passed INTEGER, total INTEGER, avg_score REAL,
        avg_seconds REAL, cost_usd REAL)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER, question TEXT, answer TEXT,
        passed INTEGER, ai_score INTEGER, seconds REAL)""")
    return conn


class RunRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    suffix: str = Field(default="", max_length=200)  # prompt addition, e.g. " Answer in one short sentence."


@app.post("/api/run")
def run(req: RunRequest):
    try:
        result = run_engine.run_all(req.suffix)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Run failed: {exc}")
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO runs (name, created_at, passed, total, avg_score, avg_seconds, cost_usd)"
            " VALUES (?,?,?,?,?,?,?)",
            (req.name, datetime.now().isoformat(timespec="seconds"), result["passed"],
             result["total"], result["avg_score"], result["avg_seconds"], result["cost_usd"]),
        )
        run_id = cur.lastrowid
        conn.executemany(
            "INSERT INTO results (run_id, question, answer, passed, ai_score, seconds) VALUES (?,?,?,?,?,?)",
            [(run_id, r["question"], r["answer"], int(r["passed"]), r["ai_score"], r["seconds"])
             for r in result["results"]],
        )
    result["id"] = run_id
    return result


@app.get("/api/runs")
def list_runs():
    with db() as conn:
        rows = conn.execute(
            "SELECT id, name, created_at, passed, total, avg_score, avg_seconds, cost_usd FROM runs ORDER BY id"
        ).fetchall()
    return [dict(r) for r in rows]


@app.get("/api/compare")
def compare(a: int, b: int):
    """Question-by-question comparison of two runs."""
    with db() as conn:
        ra = {r["question"]: r for r in conn.execute("SELECT * FROM results WHERE run_id = ?", (a,))}
        rb = {r["question"]: r for r in conn.execute("SELECT * FROM results WHERE run_id = ?", (b,))}
    if not ra or not rb:
        raise HTTPException(404, "Run not found")
    return [
        {
            "question": q,
            "a_answer": ra[q]["answer"], "b_answer": rb[q]["answer"],
            "a_passed": bool(ra[q]["passed"]), "b_passed": bool(rb[q]["passed"]),
            "a_score": ra[q]["ai_score"], "b_score": rb[q]["ai_score"],
        }
        for q in ra if q in rb
    ]


@app.get("/")
def home():
    return FileResponse("static/index.html")