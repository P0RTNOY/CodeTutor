import streamlit as st
import requests
from streamlit_ace import st_ace

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


def call_tutor(endpoint, problem_id, code, failed_test=None, question=None):
    try:
        payload = {
            "problem_id": problem_id,
            "code": code
        }

        if failed_test is not None:
            payload["failed_test"] = failed_test

        if question is not None:
            payload["question"] = question

        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=payload,
            timeout=130
        )

        response.raise_for_status()
        return response.json()["answer"]

    except requests.exceptions.RequestException as error:
        return f"Could not contact AI tutor: {error}"


def get_first_failed_test(result):
    if not result:
        return None

    for test_result in result.get("results", []):
        if not test_result.get("passed"):
            return test_result

    return None


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

if "last_run_code_by_problem" not in st.session_state:
    st.session_state.last_run_code_by_problem = {}


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
    title_suffix = " ✅ Solved" if problem["id"] in solved_problem_ids else ""
    
    st.header(f"{problem['title']}{title_suffix}")
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

    user_code = st_ace(
        value=st.session_state.code_by_problem[code_key],
        language="python",
        theme="monokai",
        key=f"editor_{code_key}",
        height=400,
        font_size=14,
        tab_size=4,
        show_gutter=True,
        show_print_margin=False,
        wrap=False,
        auto_update=True
    )

    if user_code is None:
        user_code = st.session_state.code_by_problem[code_key]

    previous_code = st.session_state.code_by_problem[code_key]
    code_changed = user_code != previous_code

    if code_changed:
        st.session_state.code_by_problem[code_key] = user_code

        if problem["id"] in st.session_state.results_by_problem:
            del st.session_state.results_by_problem[problem["id"]]

        if problem["id"] in st.session_state.tutor_answers_by_problem:
            del st.session_state.tutor_answers_by_problem[problem["id"]]

    reset_col, info_col = st.columns([1, 3])

    with reset_col:
        reset_clicked = st.button("Reset Code", use_container_width=True)

    with info_col:
        st.caption("Run Code checks visible tests. Submit checks all tests and saves your result.")

    if reset_clicked:
        st.session_state.code_by_problem[code_key] = problem["starter_code"]

        if problem["id"] in st.session_state.results_by_problem:
            del st.session_state.results_by_problem[problem["id"]]

        if problem["id"] in st.session_state.tutor_answers_by_problem:
            del st.session_state.tutor_answers_by_problem[problem["id"]]

        if problem["id"] in st.session_state.last_run_code_by_problem:
            del st.session_state.last_run_code_by_problem[problem["id"]]

        st.rerun()

    last_run_code = st.session_state.last_run_code_by_problem.get(problem["id"])

    if last_run_code is not None and last_run_code != user_code:
        st.warning("Code changed since the last run. Run again to update the results.")

    run_col, submit_col = st.columns(2)

    with run_col:
        run_clicked = st.button(
            "Run Code",
            use_container_width=True,
            help="Runs visible tests only. Does not save the submission."
        )

    with submit_col:
        submit_clicked = st.button(
            "Submit",
            use_container_width=True,
            help="Runs visible and hidden tests, then saves the submission."
        )

    if run_clicked or submit_clicked:
        endpoint = "/submit" if submit_clicked else "/run"

        st.session_state.results_by_problem[problem["id"]] = run_code(
            endpoint=endpoint,
            problem_id=problem["id"],
            code=user_code
        )

        st.session_state.last_run_code_by_problem[problem["id"]] = user_code

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

    current_result = st.session_state.results_by_problem.get(problem["id"])
    first_failed_test = get_first_failed_test(current_result)

    tutor_col1, tutor_col2 = st.columns(2)
    tutor_col3, tutor_col4 = st.columns(2)

    with tutor_col1:
        explain_clicked = st.button("Explain Problem", use_container_width=True)

    with tutor_col2:
        hint_clicked = st.button("Give Hint", use_container_width=True)

    with tutor_col3:
        review_clicked = st.button("Review My Code", use_container_width=True)

    with tutor_col4:
        debug_clicked = st.button(
            "Debug Failed Test",
            use_container_width=True,
            disabled=first_failed_test is None
        )

    if explain_clicked or hint_clicked or review_clicked or debug_clicked:
        failed_test_payload = None

        if explain_clicked:
            tutor_endpoint = "/tutor/explain-problem"
        elif hint_clicked:
            tutor_endpoint = "/tutor/hint"
        elif review_clicked:
            tutor_endpoint = "/tutor/review-code"
        else:
            tutor_endpoint = "/tutor/debug-failed-test"
            failed_test_payload = first_failed_test

        with st.spinner("CodeTutor is thinking..."):
            st.session_state.tutor_answers_by_problem[problem["id"]] = call_tutor(
                endpoint=tutor_endpoint,
                problem_id=problem["id"],
                code=user_code,
                failed_test=failed_test_payload
            )
    st.markdown("#### Ask a Custom Question")

    custom_question = st.text_input(
        "Ask CodeTutor about this problem",
        placeholder="Example: Why do we use a hash map here?",
        key=f"custom_question_{problem['id']}"
    )

    ask_clicked = st.button(
        "Ask CodeTutor",
        use_container_width=True,
        disabled=not custom_question.strip()
    )

    if ask_clicked:
        with st.spinner("CodeTutor is thinking..."):
            st.session_state.tutor_answers_by_problem[problem["id"]] = call_tutor(
                endpoint="/tutor/ask",
                problem_id=problem["id"],
                code=user_code,
                failed_test=first_failed_test,
                question=custom_question
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