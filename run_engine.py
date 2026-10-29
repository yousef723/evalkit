"""Eval logic: ask questions, check keywords, judge answers, track speed and cost."""
import json
import re
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

MODEL = "gpt-4o-mini"
PRICE_IN = 0.15 / 1_000_000   # dollars per input token (check current pricing)
PRICE_OUT = 0.60 / 1_000_000  # dollars per output token


def cost_of(usage):
    return usage.prompt_tokens * PRICE_IN + usage.completion_tokens * PRICE_OUT


def judge(question, answer, expected):
    """Returns (score 1-5, cost). Score is 0 if the judge gives no number."""
    prompt = (
        f"Score this answer 1-5.\n"
        f"Question: {question}\n"
        f"Expected keywords: {expected}\n"
        f"Answer: {answer}\n"
        "1=wrong, 5=perfect. Return ONLY a number."
    )
    reply = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    match = re.search(r"[1-5]", reply.choices[0].message.content or "")
    return (int(match.group()) if match else 0), cost_of(reply.usage)


def run_all(suffix=""):
    with open("cases.json") as f:
        cases = json.load(f)

    results = []
    for case in cases:
        start = time.time()
        reply = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": case["question"] + suffix}],
        )
        seconds = time.time() - start
        answer = reply.choices[0].message.content or ""
        passed = any(word.lower() in answer.lower() for word in case["must_contain"])
        score, judge_cost = judge(case["question"], answer, case["must_contain"])
        results.append({
            "question": case["question"],
            "answer": answer,
            "passed": passed,
            "ai_score": score,
            "seconds": round(seconds, 2),
            "cost_usd": cost_of(reply.usage) + judge_cost,
        })

    n = len(results)
    return {
        "passed": sum(r["passed"] for r in results),
        "total": n,
        "avg_score": round(sum(r["ai_score"] for r in results) / n, 2) if n else 0,
        "avg_seconds": round(sum(r["seconds"] for r in results) / n, 2) if n else 0,
        "cost_usd": round(sum(r["cost_usd"] for r in results), 6),
        "results": results,
    }