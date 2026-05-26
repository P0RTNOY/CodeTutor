from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from backend.services.problem_service import load_problem
from backend.services.tutor_service import ask_ollama, build_tutor_prompt


router = APIRouter(
    prefix="/tutor",
    tags=["Tutor"]
)


class TutorRequest(BaseModel):
    problem_id: str
    code: Optional[str] = None
    failed_test: Optional[dict] = None


@router.post("/explain-problem")
def explain_problem(request: TutorRequest):
    problem = load_problem(request.problem_id)

    if problem is None:
        raise HTTPException(
            status_code=404,
            detail=f"Problem '{request.problem_id}' was not found"
        )

    prompt = build_tutor_prompt(
        mode="explain_problem",
        problem=problem,
        code=request.code
    )

    answer = ask_ollama(prompt)

    return {
        "answer": answer
    }


@router.post("/hint")
def give_hint(request: TutorRequest):
    problem = load_problem(request.problem_id)

    if problem is None:
        raise HTTPException(
            status_code=404,
            detail=f"Problem '{request.problem_id}' was not found"
        )

    prompt = build_tutor_prompt(
        mode="hint",
        problem=problem,
        code=request.code
    )

    answer = ask_ollama(prompt)

    return {
        "answer": answer
    }


@router.post("/review-code")
def review_code(request: TutorRequest):
    problem = load_problem(request.problem_id)

    if problem is None:
        raise HTTPException(
            status_code=404,
            detail=f"Problem '{request.problem_id}' was not found"
        )

    prompt = build_tutor_prompt(
        mode="review_code",
        problem=problem,
        code=request.code
    )

    answer = ask_ollama(prompt)

    return {
        "answer": answer
    }

@router.post("/debug-failed-test")
def debug_failed_test(request: TutorRequest):
    problem = load_problem(request.problem_id)

    if problem is None:
        raise HTTPException(
            status_code=404,
            detail=f"Problem '{request.problem_id}' was not found"
        )

    if request.failed_test is None:
        raise HTTPException(
            status_code=400,
            detail="No failed test was provided"
        )

    prompt = build_tutor_prompt(
        mode="debug_failed_test",
        problem=problem,
        code=request.code,
        failed_test=request.failed_test
    )

    answer = ask_ollama(prompt)

    return {
        "answer": answer
    }