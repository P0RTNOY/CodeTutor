import streamlit as st
import requests


API_BASE_URL = "http://localhost:8000"


st.set_page_config(
    page_title="CodeTutor",
    page_icon="🧠",
    layout="wide"
)


def get_problems():
    try:
        response = requests.get(f"{API_BASE_URL}/problems", timeout=5)
        response.raise_for_status()
        return response.json()["problems"]

    except requests.exceptions.RequestException as error:
        st.error(f"Could not load problems: {error}")
        return []


def get_problem(problem_id):
    try:
        response = requests.get(f"{API_BASE_URL}/problems/{problem_id}", timeout=5)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as error:
        st.error(f"Could not load problem: {error}")
        return None


def call_tutor(endpoint, problem_id, code):
    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json={
                "problem_id": problem_id,
                "code": code
            },
            timeout=130
        )

        response.raise_for_status()
        return response.json()["answer"]

    except requests.exceptions.RequestException as error:
        return f"Could not contact AI tutor: {error}"


def run_code(endpoint, problem_id, code):
    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json={
                "problem_id": problem_id,
                "code": code
            },
            timeout=10
        )

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as error:
        return {
            "status": "error",
            "message": f"Could not run code: {error}",
            "results": []
        }

def get_submission_history(problem_id):
    try:
        response = requests.get(
            f"{API_BASE_URL}/submissions/{problem_id}",
            timeout=5
        )

        response.raise_for_status()
        return response.json()["submissions"]

    except requests.exceptions.RequestException:
        return []


def get_progress():
    try:
        response = requests.get(
            f"{API_BASE_URL}/progress",
            timeout=5
        )

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException:
        return {
            "total_problems": 0,
            "solved_total": 0,
            "progress_percent": 0,
            "solved_problem_ids": [],
            "by_difficulty": {}
        }


def difficulty_badge(difficulty):
    if difficulty == "Easy":
        return "🟢 Easy"

    if difficulty == "Medium":
        return "🟡 Medium"

    if difficulty == "Hard":
        return "🔴 Hard"

    return difficulty


if "code_by_problem" not in st.session_state:
    st.session_state.code_by_problem = {}

if "results_by_problem" not in st.session_state:
    st.session_state.results_by_problem = {}

if "tutor_answers_by_problem" not in st.session_state:
    st.session_state.tutor_answers_by_problem = {}


st.title("CodeTutor")
st.caption("Practice coding problems with an AI tutor.")


problems = get_problems()

if not problems:
    st.warning("No problems found.")
    st.stop()

progress = get_progress()
solved_problem_ids = set(progress["solved_problem_ids"])


with st.sidebar:
    st.header("Problems")
    
    st.subheader("Progress")

    solved_total = progress["solved_total"]
    total_problems = progress["total_problems"]
    progress_percent = progress["progress_percent"]

    st.write(f"**Solved:** {solved_total} / {total_problems}")
    st.progress(progress_percent / 100)

    for difficulty, data in progress["by_difficulty"].items():
        st.caption(
            f"{difficulty}: {data['solved']} / {data['total']}"
        )

    st.divider()
    

    difficulties = ["All"] + sorted(
        list({problem["difficulty"] for problem in problems})
    )

    selected_difficulty = st.selectbox(
        "Filter by difficulty",
        difficulties
    )

    if selected_difficulty == "All":
        filtered_problems = problems
    else:
        filtered_problems = [
            problem for problem in problems
            if problem["difficulty"] == selected_difficulty
        ]

    st.write(f"Showing **{len(filtered_problems)}** of **{len(problems)}** problems")

    problem_labels = {}

    for problem in filtered_problems:
        solved_prefix = "✅ " if problem["id"] in solved_problem_ids else ""
        label = f"{solved_prefix}{problem['title']} — {problem['difficulty']}"
        problem_labels[label] = problem["id"]

    selected_label = st.selectbox(
        "Choose a problem",
        list(problem_labels.keys())
    )


selected_problem_id = problem_labels[selected_label]
problem = get_problem(selected_problem_id)

if problem is None:
    st.stop()


code_key = problem["id"]

if code_key not in st.session_state.code_by_problem:
    st.session_state.code_by_problem[code_key] = problem["starter_code"]


left_col, right_col = st.columns([1, 1])


with left_col:
    st.header(problem["title"])

    st.write(f"**Difficulty:** {difficulty_badge(problem['difficulty'])}")
    st.write(f"**Tags:** {', '.join(problem['tags'])}")

    st.divider()

    st.subheader("Description")
    st.write(problem["description"])

    st.subheader("Examples")

    for index, example in enumerate(problem["examples"], start=1):
        with st.expander(f"Example {index}", expanded=True):
            st.code(
                f"Input: {example['input']}\nOutput: {example['output']}"
            )

            if "explanation" in example:
                st.write(f"**Explanation:** {example['explanation']}")


with right_col:
    st.subheader("Your Python Solution")

    user_code = st.text_area(
        label="Code",
        value=st.session_state.code_by_problem[code_key],
        height=400,
        key=f"editor_{code_key}"
    )

    st.session_state.code_by_problem[code_key] = user_code

    run_col, submit_col = st.columns(2)

    with run_col:
        run_clicked = st.button("Run Code", use_container_width=True)

    with submit_col:
        submit_clicked = st.button("Submit", use_container_width=True)

    if run_clicked or submit_clicked:
        endpoint = "/submit" if submit_clicked else "/run"

        st.session_state.results_by_problem[problem["id"]] = run_code(
            endpoint=endpoint,
            problem_id=problem["id"],
            code=user_code
        )

        if submit_clicked:
            st.rerun()

    current_result = st.session_state.results_by_problem.get(problem["id"])

    if current_result:
        result = current_result

        st.divider()
        st.subheader("Test Results")

        if result["status"] == "passed":
            st.success("All tests passed!")
        elif result["status"] == "failed":
            st.error("Some tests failed.")
        else:
            st.error(result.get("message", "Something went wrong."))

        if "error" in result:
            st.code(result["error"])

        for test_result in result.get("results", []):
            title = f"Test {test_result['test_number']}"

            if test_result["passed"]:
                title += " — Passed"
            else:
                title += " — Failed"

            with st.expander(title, expanded=not test_result["passed"]):
                st.write("**Input:**")
                st.json(test_result["input"])

                st.write("**Expected:**")
                st.json(test_result["expected"])

                st.write("**Actual:**")
                st.json(test_result["actual"])

                if test_result["error"]:
                    st.write("**Error:**")
                    st.code(test_result["error"])

    st.divider()
    st.subheader("AI Tutor")

    tutor_col1, tutor_col2, tutor_col3 = st.columns(3)

    with tutor_col1:
        explain_clicked = st.button("Explain Problem", use_container_width=True)

    with tutor_col2:
        hint_clicked = st.button("Give Hint", use_container_width=True)

    with tutor_col3:
        review_clicked = st.button("Review My Code", use_container_width=True)

    if explain_clicked or hint_clicked or review_clicked:
        if explain_clicked:
            tutor_endpoint = "/tutor/explain-problem"
        elif hint_clicked:
            tutor_endpoint = "/tutor/hint"
        else:
            tutor_endpoint = "/tutor/review-code"

        with st.spinner("CodeTutor is thinking..."):
            st.session_state.tutor_answers_by_problem[problem["id"]] = call_tutor(
                endpoint=tutor_endpoint,
                problem_id=problem["id"],
                code=user_code
            )

    current_tutor_answer = st.session_state.tutor_answers_by_problem.get(problem["id"])

    if current_tutor_answer:
        st.markdown("### Tutor Response")
        st.write(current_tutor_answer)

    st.divider()
    st.subheader("Submission History")

    history = get_submission_history(problem["id"])

    if not history:
        st.info("No submissions yet for this problem.")
    else:
        for submission in history[:5]:
            status = submission["status"]
            passed_tests = submission["passed_tests"]
            total_tests = submission["total_tests"]
            created_at = submission["created_at"]

            if status == "passed":
                st.success(
                    f"{created_at} — Passed ({passed_tests}/{total_tests})"
                )
            else:
                st.error(
                    f"{created_at} — {status.title()} ({passed_tests}/{total_tests})"
                )