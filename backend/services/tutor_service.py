from typing import Optional
import requests


OLLAMA_URL = "http://localhost:11434/v1/chat/completions"
MODEL_NAME = "llama3.2"


SYSTEM_PROMPT = """
You are CodeTutor, an AI tutor inside a coding practice platform.

Your job is to guide the user step by step.

Rules:
1. Do not immediately reveal the full solution.
2. Give small hints first.
3. Ask guiding questions when useful.
4. Use simple examples.
5. If user code is provided, analyze their code directly.
6. If there is a failed test case, explain why the output differs.
7. Only provide a complete solution when the user explicitly asks for it.
8. Explain time and space complexity only after the approach is understood.
9. Be clear, practical, and beginner-friendly.
"""


def ask_ollama(user_prompt: str):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "temperature": 0.3
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"]


def build_tutor_prompt(
    mode: str,
    problem: dict,
    code: Optional[str] = None,
    failed_test: Optional[dict] = None
):
    base_prompt = f"""
Problem title:
{problem["title"]}

Difficulty:
{problem["difficulty"]}

Tags:
{", ".join(problem["tags"])}

Description:
{problem["description"]}

Examples:
{problem["examples"]}
"""

    if mode == "explain_problem":
        return base_prompt + """

Task:
Explain this problem in simple words.
Do not give the full solution yet.
Explain what the input means, what the output means, and what the user needs to find.
"""

    if mode == "hint":
        return base_prompt + """

Task:
Give one helpful hint for solving this problem.
Do not give the full solution.
Do not write code.
"""

    if mode == "review_code":
        return base_prompt + f"""

User code:
{code}

Task:
Review the user's code.
Explain what is good, what may be wrong, and give one concrete next step.
Do not rewrite the entire solution unless absolutely necessary.
"""

    if mode == "debug_failed_test":
        return base_prompt + f"""

User code:
{code}

Failed test:
{failed_test}

Task:
Explain why this specific test failed.

Rules:
1. Focus on the failed test, not the whole problem.
2. Explain the expected output versus the actual output.
3. Point to the likely bug in the user's logic.
4. Give one concrete next step.
5. Do not provide the full corrected solution unless the user explicitly asks.
"""

    return base_prompt + """

Task:
Help the user understand this problem.
"""