import json
import sqlite3
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

DB = "evals.db"


def judge(question, answer, expected):
    """Ask the AI to score the answer 1-5."""
    prompt = (
        f"Score this answer 1-5.\n"
        f"Question: {question}\n"
        f"Expected keywords: {expected}\n"
        f"Answer: {answer}\n"
        "1=wrong, 5=perfect. Return ONLY a number."
    )
    reply = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    try:
        return int(reply.choices[0].message.content.strip())
    except (ValueError, TypeError):
        return 0


def db():
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, created_at TEXT,
        passed INTEGER, total INTEGER, avg_score REAL)""")
    return conn


with open("cases.json") as f:
    cases = json.load(f)

run_name = input("Run name (e.g. baseline): ").strip() or "unnamed"

results = []
for case in cases:
    reply = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": case["question"] + " Answer in one short sentence."}],
    )
    answer = reply.choices[0].message.content
    passed = any(word.lower() in answer.lower() for word in case["must_contain"])
    score = judge(case["question"], answer, case["must_contain"])
    results.append({
        "question": case["question"],
        "answer": answer,
        "passed": passed,
        "ai_score": score,
    })
    print("PASS" if passed else "FAIL", "| score:", score, "|", case["question"])

with open("results.json", "w") as f:
    json.dump(results, f, indent=2)

total = sum(r["passed"] for r in results)
avg_score = sum(r["ai_score"] for r in results) / len(results) if results else 0
print(f"\n{total} of {len(results)} passed | avg AI score: {avg_score:.1f}/5")

with db() as conn:
    conn.execute(
        "INSERT INTO runs (name, created_at, passed, total, avg_score) VALUES (?,?,?,?,?)",
        (run_name, datetime.now().isoformat(timespec="seconds"), total, len(results), avg_score),
    )

print(f"Saved run '{run_name}' to {DB}")