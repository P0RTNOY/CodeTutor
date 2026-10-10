# CodeTutor

CodeTutor is a Python-based LeetCode-style coding practice platform with an integrated AI tutor.

The app allows users to choose coding problems, write Python solutions in an IDE-like editor, run visible tests, submit against hidden tests, track solved progress, and ask an AI tutor for guided help.

The project is built as a portfolio-level full-stack Python application using FastAPI, Streamlit, SQLite, Ollama, and a local problem bank.

---

## Overview

CodeTutor is designed to help users practice algorithmic problem solving while receiving step-by-step guidance from an AI tutor.

Unlike a normal coding judge, CodeTutor does not only say whether a solution passed or failed. It can also:

* Explain the problem in simple words
* Give hints without revealing the full solution
* Review the user's code
* Debug a specific failed test case
* Answer custom user questions about the problem or solution
* Track solved problems and submission history

The goal is to combine the coding-practice experience of platforms like LeetCode with an interactive AI learning assistant.

---

## Features

### Coding Practice

* Problem bank loaded from local JSON files
* Problem selector with difficulty filtering
* Problem descriptions, examples, tags, and starter code
* Python code editor with:

  * Syntax highlighting
  * Line numbers
  * Proper Tab indentation
  * Dark editor theme
* Run Code button for visible tests
* Submit button for visible and hidden tests
* Test result display with:

  * Accepted
  * Wrong Answer
  * Runtime Error
  * Per-test input, expected output, and actual output

---

### AI Tutor

CodeTutor includes an AI tutor powered by a local Ollama-compatible model.

The tutor supports:

* Explain Problem
* Give Hint
* Review My Code
* Debug Failed Test
* Custom question input
* Per-problem tutor response history
* Clear tutor history action

The tutor is designed to guide the user step by step instead of immediately giving away the full solution.

---

### Progress Tracking

CodeTutor stores submissions in SQLite and tracks progress automatically.

The app shows:

* Total solved problems
* Progress percentage
* Difficulty-level progress
* Solved badges in the problem dropdown
* Solved status on the problem page
* Latest submission history per problem

A problem is considered solved once it has at least one saved submission with status `passed`.

---

## Tech Stack

### Backend

* Python
* FastAPI
* Pydantic
* SQLite
* Uvicorn

### Frontend

* Streamlit
* streamlit-ace

### AI

* Ollama local server
* OpenAI-compatible Ollama endpoint

### Storage

* Local JSON files for coding problems
* SQLite database for submission history

---

## Project Structure

```txt
ai-leetcode-tutor/
│
├── backend/
│   ├── main.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   └── codetutor.db
│   │
│   ├── problems/
│   │   ├── two_sum.json
│   │   ├── valid_parentheses.json
│   │   ├── best_time_to_buy_stock.json
│   │   ├── contains_duplicate.json
│   │   ├── reverse_string.json
│   │   └── maximum_subarray.json
│   │
│   ├── routers/
│   │   ├── problems.py
│   │   ├── submissions.py
│   │   └── tutor.py
│   │
│   └── services/
│       ├── problem_service.py
│       ├── execution_service.py
│       ├── submission_service.py
│       └── tutor_service.py
│
├── frontend/
│   └── app.py
│
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd ai-leetcode-tutor
```

If you are working locally without a remote repository yet, simply open the project folder in your IDE.

---

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include:

```txt
fastapi
uvicorn
streamlit
requests
pydantic
streamlit-ace
```

---

## Ollama Setup

CodeTutor uses a local Ollama server for AI tutoring.

### 1. Install Ollama

Download and install Ollama from the official Ollama website.

After installation, verify that Ollama works:

```bash
ollama --version
```

---

### 2. Pull a Model

For lightweight local testing:

```bash
ollama pull llama3.2
```

If you want to use another model, update the model name in:

```txt
backend/services/tutor_service.py
```

Current default:

```python
MODEL_NAME = "llama3.2"
```

---

### 3. Make Sure Ollama Is Running

Ollama usually runs locally at:

```txt
http://localhost:11434
```

CodeTutor uses the OpenAI-compatible endpoint:

```txt
http://localhost:11434/v1/chat/completions
```

---

## Running the App

You need to run the backend and frontend in two separate terminals.

---

### Terminal 1 — Start FastAPI Backend

From the project root:

```bash
uvicorn backend.main:app --reload --port 8000
```

Backend URL:

```txt
http://localhost:8000
```

Health check:

```txt
http://localhost:8000/health
```

API docs:

```txt
http://localhost:8000/docs
```

---

### Terminal 2 — Start Streamlit Frontend

From the project root:

```bash
streamlit run frontend/app.py
```

Streamlit will open the app in the browser.

Default URL is usually:

```txt
http://localhost:8501
```

---

## API Endpoints

### General

```txt
GET /
GET /health
```

---

### Problems

```txt
GET /problems
GET /problems/{problem_id}
```

Example:

```txt
GET /problems/two_sum
```

---

### Code Execution

```txt
POST /run
POST /submit
```

`/run` executes only visible tests.

`/submit` executes visible and hidden tests, then saves the submission to SQLite.

Example request:

```json
{
  "problem_id": "two_sum",
  "code": "def two_sum(nums, target):\n    pass"
}
```

---

### Submission History

```txt
GET /submissions/{problem_id}
GET /progress
```

Example:

```txt
GET /submissions/two_sum
```

---

### AI Tutor

```txt
POST /tutor/explain-problem
POST /tutor/hint
POST /tutor/review-code
POST /tutor/debug-failed-test
POST /tutor/ask
```

Example request:

```json
{
  "problem_id": "two_sum",
  "code": "def two_sum(nums, target):\n    pass",
  "question": "Why do we use a hash map here?"
}
```

---

## Problem JSON Format

Problems are stored as JSON files inside:

```txt
backend/problems/
```

Example structure:

```json
{
  "id": "two_sum",
  "title": "Two Sum",
  "difficulty": "Easy",
  "tags": ["Array", "Hash Map"],
  "description": "Given a list of integers nums and an integer target, return the indices of the two numbers such that they add up to target.",
  "function_name": "two_sum",
  "starter_code": "def two_sum(nums, target):\n    pass",
  "examples": [
    {
      "input": "nums = [2, 7, 11, 15], target = 9",
      "output": "[0, 1]",
      "explanation": "nums[0] + nums[1] = 2 + 7 = 9"
    }
  ],
  "visible_tests": [
    {
      "input": {
        "nums": [2, 7, 11, 15],
        "target": 9
      },
      "expected": [0, 1]
    }
  ],
  "hidden_tests": [
    {
      "input": {
        "nums": [3, 3],
        "target": 6
      },
      "expected": [0, 1]
    }
  ]
}
```

---

## Current Problems

CodeTutor currently includes:

| Problem                         | Difficulty | Tags                       |
| ------------------------------- | ---------- | -------------------------- |
| Two Sum                         | Easy       | Array, Hash Map            |
| Valid Parentheses               | Easy       | Stack, String              |
| Best Time to Buy and Sell Stock | Easy       | Array, Dynamic Programming |
| Contains Duplicate              | Easy       | Array, Hash Set            |
| Reverse String                  | Easy       | Two Pointers, String       |
| Maximum Subarray                | Medium     | Array, Dynamic Programming |

---

## How Code Execution Works

When the user clicks Run Code or Submit:

1. The frontend sends the code and problem ID to FastAPI.
2. The backend loads the selected problem JSON.
3. The backend executes the user's Python function.
4. The backend calls the function with each test input.
5. The actual output is compared to the expected output.
6. The result is returned to the frontend.
7. If the user clicked Submit, the result is also saved to SQLite.

---

## Important Security Note

The current version executes user code locally using Python's `exec()`.

This is acceptable for local learning and development, but it is not safe for a public production app.

Before exposing CodeTutor to real users, code execution should be moved into a secure sandbox, such as:

* Docker container execution
* Network disabled
* CPU limit
* Memory limit
* Timeout limit
* Temporary isolated filesystem

Planned future improvement:

```txt
Move execution into Docker sandbox
```

---

## SQLite Database

The SQLite database is initialized automatically when FastAPI starts.

Database file:

```txt
backend/db/codetutor.db
```

The database currently stores submissions in the `submissions` table.

Current submission fields:

```txt
id
problem_id
code
status
total_tests
passed_tests
created_at
```

---

## AI Tutor Behavior

The AI tutor is instructed to act as a coding mentor.

Its main rules are:

* Guide the user step by step
* Give hints before full solutions
* Use simple examples
* Review the user's actual code
* Explain failed tests when available
* Avoid giving the full answer unless the user explicitly asks for it

The system prompt is located in:

```txt
backend/services/tutor_service.py
```

---

## Main User Flow

1. User opens CodeTutor.
2. User selects a coding problem.
3. User reads the problem description and examples.
4. User writes Python code in the Ace editor.
5. User clicks Run Code to test visible tests.
6. User sees test results.
7. If a test fails, the user can click Debug Failed Test.
8. User can ask the AI tutor questions.
9. User clicks Submit to run hidden tests and save the submission.
10. Progress and solved status update automatically.

---

## Development Roadmap

### Completed

* FastAPI backend
* Streamlit frontend
* Local JSON problem bank
* Code editor with Ace
* Visible test execution
* Hidden test submission
* SQLite submission history
* Progress tracking
* Solved badges
* AI tutor with Ollama
* Debug failed test mode
* Custom AI tutor questions
* Tutor response history
* Improved tab-based UI

---

### Planned Improvements

* Docker-based safe code execution
* Timeout protection for infinite loops
* Better error classification
* Environment variable configuration
* Add more problems
* Add constraints section to problem JSON
* Add full solution view
* Add user authentication
* Add user profiles
* Add difficulty and tag statistics
* Add multi-language support
* Add deployment instructions

---

## Useful Commands

### Start Backend

```bash
uvicorn backend.main:app --reload --port 8000
```

### Start Frontend

```bash
streamlit run frontend/app.py
```

### Install Requirements

```bash
pip install -r requirements.txt
```

### Check Ollama

```bash
ollama --version
```

### List Ollama Models

```bash
ollama list
```

### Pull Model

```bash
ollama pull llama3.2
```

---

## Suggested Git Workflow

After completing a feature:

```bash
git add .
git commit -m "Describe the completed feature"
```

Example commits used during development:

```bash
git commit -m "Add initial problem bank with multiple coding challenges"
git commit -m "Improve Streamlit UI with filters and per-problem code state"
git commit -m "Store test results and tutor responses per problem"
git commit -m "Add SQLite submission history"
git commit -m "Add solved status and progress summary"
git commit -m "Add AI tutor debug mode for failed tests"
git commit -m "Add custom question support to AI tutor"
git commit -m "Upgrade code input to Ace editor"
git commit -m "Improve coding workspace UX"
git commit -m "Add AI tutor response history"
git commit -m "Refactor workspace UI into tabs"
```

---

## Troubleshooting

### Backend is not connected

Make sure FastAPI is running:

```bash
uvicorn backend.main:app --reload --port 8000
```

Then check:

```txt
http://localhost:8000/health
```

---

### Streamlit cannot load problems

Make sure the backend is running before starting Streamlit.

Also check:

```txt
http://localhost:8000/problems
```

---

### AI Tutor does not respond

Check that Ollama is installed:

```bash
ollama --version
```

Check that a model exists:

```bash
ollama list
```

Pull a model if needed:

```bash
ollama pull llama3.2
```

Make sure the model name in `backend/services/tutor_service.py` matches the installed model.

---

### Reset Code does not visually reset the editor

The app uses `editor_versions` in Streamlit session state to force the Ace editor to reload.

If reset does not work, check that the Ace editor key includes the editor version:

```python
key=f"editor_{code_key}_{st.session_state.editor_versions[code_key]}"
```

---

### Infinite loop freezes execution

The current local execution system does not fully protect against infinite loops.

This is a known limitation.

Planned fix:

```txt
Move code execution into Docker with timeout, memory, CPU, and network limits.
```

---

## Notes

This project is intended as a learning and portfolio project.

It demonstrates:

* Python backend development
* API design
* Streamlit UI development
* Local AI model integration
* Prompt engineering
* SQLite persistence
* Code execution logic
* Algorithmic problem modeling
* State management in Streamlit

CodeTutor is not production-ready yet because user code execution still needs sandboxing.

---

## Author

Created by Omer Portnoy as a Python-based AI coding tutor and LeetCode-style practice platform.
