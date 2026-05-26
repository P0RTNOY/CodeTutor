# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException

from backend.services.problem_service import load_all_problems, load_problem

router = APIRouter(
    prefix="/problems",
    tags=["Problems"]
)

@router.get("")

def get_problems():
    return {
        "problems": load_all_problems()
    }

@router.get("/{problem_id}")
def get_problem(problem_id: str):
    problem = load_problem(problem_id)
    if problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem