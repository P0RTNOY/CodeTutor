import traceback
from backend.services.problem_service import load_problem


def run_user_code(problem_id: str, code: str, use_hidden_tests: bool = False):
    problem = load_problem(problem_id)

    if problem is None:
        return {
            "status": "error",
            "message": f"Problem '{problem_id}' was not found",
            "results": []
        }

    function_name = problem["function_name"]

    tests = list(problem["visible_tests"])

    if use_hidden_tests:
        tests += problem.get("hidden_tests", [])

    local_namespace = {}

    try:
        exec(code, {}, local_namespace)
    except Exception as error:
        return {
            "status": "error",
            "message": "Your code has a syntax/runtime error before tests could run.",
            "error": str(error),
            "traceback": traceback.format_exc(),
            "results": []
        }

    if function_name not in local_namespace:
        return {
            "status": "error",
            "message": f"Function '{function_name}' was not found in your code.",
            "results": []
        }

    user_function = local_namespace[function_name]
    results = []

    for index, test in enumerate(tests, start=1):
        test_input = test["input"]
        expected = test["expected"]

        try:
            actual = user_function(**test_input)
            passed = actual == expected

            results.append({
                "test_number": index,
                "passed": passed,
                "input": test_input,
                "expected": expected,
                "actual": actual,
                "error": None
            })

        except Exception as error:
            results.append({
                "test_number": index,
                "passed": False,
                "input": test_input,
                "expected": expected,
                "actual": None,
                "error": str(error)
            })

    all_passed = all(result["passed"] for result in results)

    return {
        "status": "passed" if all_passed else "failed",
        "results": results
    }