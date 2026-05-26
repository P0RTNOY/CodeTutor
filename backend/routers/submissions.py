from pydantic import BaseModel
from fastapi import APIRouter

from backend.services.execution_service import run_user_code


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
    return run_user_code(
        problem_id=request.problem_id,
        code=request.code,
        use_hidden_tests=True
    )