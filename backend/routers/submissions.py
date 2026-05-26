from pydantic import BaseModel
from fastapi import APIRouter
from backend.services.problem_service import load_all_problems

from backend.services.execution_service import run_user_code
from backend.services.submission_service import (
    save_submission,
    get_submissions_by_problem,
    get_progress_summary
)


router = APIRouter(
    tags=["Submissions"]
)


class RunCodeRequest(BaseModel):
    problem_id: str
    code: str


@router.post("/run")
def run_code(request: RunCodeRequest):
    return run_user_code(
        problem_id=request.problem_id,
        code=request.code,
        use_hidden_tests=False
    )


@router.post("/submit")
def submit_code(request: RunCodeRequest):
    result = run_user_code(
        problem_id=request.problem_id,
        code=request.code,
        use_hidden_tests=True
    )

    save_submission(
        problem_id=request.problem_id,
        code=request.code,
        result=result
    )

    return result


@router.get("/submissions/{problem_id}")
def get_problem_submissions(problem_id: str):
    return {
        "submissions": get_submissions_by_problem(problem_id)
    }

@router.get("/progress")
def get_progress():
    problems = load_all_problems()

    return get_progress_summary(problems)