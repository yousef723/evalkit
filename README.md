# EvalKit

A small tool for testing AI prompts. It runs the same set of questions against an LLM with different prompts, scores every answer, and shows which prompt is better, cheaper, or faster.

## What it does
- Runs a list of test questions (`cases.json`) against an OpenAI model with a prompt of your choice
- Checks each answer with a keyword rule and scores it 1-5 with an AI judge
- Saves every run to SQLite: pass rate, average score, speed, cost, and each question's answer
- Compares two runs side by side, question by question, with changed results highlighted

## Stack
Python, FastAPI, SQLite, OpenAI API, plain HTML/JS front end.

## Run it
```
pip install fastapi uvicorn openai python-dotenv
```
Create a `.env` file next to `app.py`:
```
OPENAI_API_KEY=your-key-here
```
Start the server and open http://127.0.0.1:8000:
```
python -m uvicorn app:app --reload
```
Enter a run name and a prompt suffix (text added to every question), click **Run**, make a second run with a different prompt, then pick both and click **Compare**.

## Test cases
`cases.json` is a list of questions, each with words the answer should contain:
```json
{"question": "What is the capital of France?", "must_contain": ["Paris"]}
```
A case passes if the answer contains any word in `must_contain`.

## Example result
On 21 general-knowledge questions, a prompt asking for two-sentence explanations scored the same as one asking for a short sentence (16 of 21 passed, average judge score 4.62 for both), but cost about 2.5x more ($0.0010 against $0.0004 per run).

The tool also caught a model limitation: asked who the current US president is, the model answered from out-of-date training data.

## Files
- `app.py`: FastAPI backend and database
- `run_engine.py`: runs the questions, checks keywords, judges answers, tracks cost and speed
- `static/index.html`: the web page
- `cases.json`: the test questions

## Limitations
- The keyword check is simple and can miss correct answers that use different wording (for example "5,040" for 5040)
- The same model answers the questions and judges them, so judge scores can be biased
- Results vary slightly between runs because LLM answers are not identical every time
- Cost is estimated from token counts using fixed prices, so update the prices in `run_engine.py` if OpenAI changes them
