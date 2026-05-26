from backend.db.database import get_connection


def save_submission(problem_id: str, code: str, result: dict):
    results = result.get("results", [])
    total_tests = len(results)
    passed_tests = sum(1 for test in results if test.get("passed"))

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO submissions (
            problem_id,
            code,
            status,
            total_tests,
            passed_tests
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            problem_id,
            code,
            result.get("status", "error"),
            total_tests,
            passed_tests
        )
    )

    connection.commit()
    connection.close()


def get_submissions_by_problem(problem_id: str):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            problem_id,
            status,
            total_tests,
            passed_tests,
            created_at
        FROM submissions
        WHERE problem_id = ?
        ORDER BY created_at DESC
        """,
        (problem_id,)
    )

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]

def get_solved_problem_ids():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT DISTINCT problem_id
        FROM submissions
        WHERE status = 'passed'
        """
    )

    rows = cursor.fetchall()
    connection.close()

    return [row["problem_id"] for row in rows]


def get_progress_summary(problems: list[dict]):
    solved_problem_ids = set(get_solved_problem_ids())

    total_problems = len(problems)
    solved_total = sum(
        1 for problem in problems
        if problem["id"] in solved_problem_ids
    )

    by_difficulty = {}

    for problem in problems:
        difficulty = problem["difficulty"]

        if difficulty not in by_difficulty:
            by_difficulty[difficulty] = {
                "total": 0,
                "solved": 0
            }

        by_difficulty[difficulty]["total"] += 1

        if problem["id"] in solved_problem_ids:
            by_difficulty[difficulty]["solved"] += 1

    progress_percent = 0

    if total_problems > 0:
        progress_percent = round((solved_total / total_problems) * 100, 1)

    return {
        "total_problems": total_problems,
        "solved_total": solved_total,
        "progress_percent": progress_percent,
        "solved_problem_ids": list(solved_problem_ids),
        "by_difficulty": by_difficulty
    }