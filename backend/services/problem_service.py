import json
from pathlib import Path

PROBLEMS_DIR = Path(__file__).resolve().parent.parent / "problems"

def load_problem(problem_id:str):
    problem_path = PROBLEMS_DIR / f"{problem_id}.json"
    if not problem_path.exists():
        return None
    with open(problem_path, "r", encoding="utf-8") as file:
        return json.load(file)

def load_all_problems():
    problems = []
    for problem_file in PROBLEMS_DIR.glob("*.json"):
        with open(problem_file, "r", encoding="utf-8") as file:
            problem = json.load(file)

            problems.append({
                "id": problem["id"],
                "title": problem["title"],
                "difficulty": problem["difficulty"],
                "tags": problem["tags"],
            })
    return problems
            
    
    