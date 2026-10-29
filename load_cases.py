import json

with open("cases.json") as f:
    cases = json.load(f)

for case in cases:
    print(case["question"], "->", case["must_contain"])