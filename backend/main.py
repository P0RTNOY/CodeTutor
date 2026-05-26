from fastapi import FastAPI

from backend.db.database import init_db
from backend.routers.problems import router as problems_router
from backend.routers.submissions import router as submissions_router
from backend.routers.tutor import router as tutor_router


app = FastAPI(title="CodeTutor API")

init_db()

app.include_router(problems_router)
app.include_router(submissions_router)
app.include_router(tutor_router)


@app.get("/")
def root():
    return {
        "message": "CodeTutor API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }