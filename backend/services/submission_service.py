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