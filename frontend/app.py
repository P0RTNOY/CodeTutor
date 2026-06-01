from datetime import datetime
import streamlit as st
import requests
from streamlit_ace import st_ace


API_BASE_URL = "http://localhost:8000"


st.set_page_config(
    page_title="CodeTutor",
    page_icon="🧠",
    layout="wide"
)


# ── Helper functions ────────────────────────────────────────────────────────────

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
        payload = {"problem_id": problem_id, "code": code}
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


def add_tutor_answer(problem_id, answer_type, answer, question=None):
    if problem_id not in st.session_state.tutor_answers_by_problem:
        st.session_state.tutor_answers_by_problem[problem_id] = []

    entry = {
        "type": answer_type,
        "question": question,
        "answer": answer,
        "created_at": datetime.now().strftime("%H:%M:%S")
    }

    st.session_state.tutor_answers_by_problem[problem_id].insert(0, entry)
    st.session_state.tutor_answers_by_problem[problem_id] = (
        st.session_state.tutor_answers_by_problem[problem_id][:5]
    )


def run_code(endpoint, problem_id, code):
    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json={"problem_id": problem_id, "code": code},
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
        response = requests.get(f"{API_BASE_URL}/progress", timeout=5)
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


def status_label(status):
    """Return an emoji-prefixed label for a submission status string."""
    if status == "passed":
        return "✅ Passed"
    if status == "failed":
        return "❌ Failed"
    if status == "error":
        return "⚠️ Error"
    return status.title()


# ── Session state initialisation ───────────────────────────────────────────────

if "code_by_problem" not in st.session_state:
    st.session_state.code_by_problem = {}

if "results_by_problem" not in st.session_state:
    st.session_state.results_by_problem = {}

if "tutor_answers_by_problem" not in st.session_state:
    st.session_state.tutor_answers_by_problem = {}

if "last_run_code_by_problem" not in st.session_state:
    st.session_state.last_run_code_by_problem = {}

if "editor_versions" not in st.session_state:
    st.session_state.editor_versions = {}


# ── App header ──────────────────────────────────────────────────────────────────

st.title("🧠 CodeTutor")
st.caption("Practice coding problems with an AI tutor.")


# ── Load data ───────────────────────────────────────────────────────────────────

problems = get_problems()

if not problems:
    st.warning("No problems found.")
    st.stop()

progress = get_progress()
solved_problem_ids = set(progress["solved_problem_ids"])


# ── Sidebar ─────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("📚 Problems")

    # Progress summary
    solved_total = progress["solved_total"]
    total_problems = progress["total_problems"]
    progress_percent = progress["progress_percent"]

    st.metric("Progress", f"{solved_total} / {total_problems} solved")
    st.progress(progress_percent / 100)

    by_diff = progress.get("by_difficulty", {})
    if by_diff:
        diff_lines = []
        for diff, data in by_diff.items():
            badge = difficulty_badge(diff)
            diff_lines.append(f"{badge}: {data['solved']}/{data['total']}")
        st.caption("  ·  ".join(diff_lines))

    st.divider()

    # Difficulty filter
    difficulties = ["All"] + sorted(
        list({problem["difficulty"] for problem in problems})
    )
    selected_difficulty = st.selectbox("Filter by difficulty", difficulties)

    if selected_difficulty == "All":
        filtered_problems = problems
    else:
        filtered_problems = [
            p for p in problems if p["difficulty"] == selected_difficulty
        ]

    st.caption(f"Showing {len(filtered_problems)} of {len(problems)} problems")

    # Problem picker with solved badges
    problem_labels = {}
    for problem in filtered_problems:
        solved_prefix = "✅ " if problem["id"] in solved_problem_ids else ""
        diff_icon = difficulty_badge(problem["difficulty"]).split()[0]  # emoji only
        label = f"{solved_prefix}{problem['title']} {diff_icon}"
        problem_labels[label] = problem["id"]

    selected_label = st.selectbox("Choose a problem", list(problem_labels.keys()))


# ── Load selected problem ───────────────────────────────────────────────────────

selected_problem_id = problem_labels[selected_label]
problem = get_problem(selected_problem_id)

if problem is None:
    st.stop()

code_key = problem["id"]

if code_key not in st.session_state.code_by_problem:
    st.session_state.code_by_problem[code_key] = problem["starter_code"]

if code_key not in st.session_state.editor_versions:
    st.session_state.editor_versions[code_key] = 0


# ── Two-column layout ───────────────────────────────────────────────────────────

left_col, right_col = st.columns([1, 1])


# ── Left column: Problem description ───────────────────────────────────────────

with left_col:
    is_solved = problem["id"] in solved_problem_ids
    solved_badge = "  ✅ Solved" if is_solved else ""

    st.subheader(f"{problem['title']}{solved_badge}")

    # Difficulty + tags on the same row
    meta_col1, meta_col2 = st.columns([1, 2])
    with meta_col1:
        st.write(difficulty_badge(problem["difficulty"]))
    with meta_col2:
        tags = problem.get("tags", [])
        if tags:
            st.caption("🏷️ " + "  ·  ".join(tags))

    st.divider()

    st.markdown("**Description**")
    st.write(problem["description"])

    st.markdown("**Examples**")
    for index, example in enumerate(problem["examples"], start=1):
        with st.expander(f"Example {index}"):
            st.code(
                f"Input:  {example['input']}\nOutput: {example['output']}"
            )
            if "explanation" in example:
                st.caption(f"💡 {example['explanation']}")


# ── Right column: Tabbed interface ──────────────────────────────────────────────

with right_col:
    code_tab, tutor_tab, history_tab = st.tabs(["💻 Code", "🤖 AI Tutor", "📋 Submissions"])

    # ── Code tab ───────────────────────────────────────────────────────────────
    with code_tab:
        st.markdown("**Your Python Solution**")

        user_code = st_ace(
            value=st.session_state.code_by_problem[code_key],
            language="python",
            theme="monokai",
            key=f"editor_{code_key}_{st.session_state.editor_versions[code_key]}",
            height=380,
            font_size=14,
            tab_size=4,
            show_gutter=True,
            show_print_margin=False,
            wrap=False,
            auto_update=True
        )

        if user_code is None:
            user_code = st.session_state.code_by_problem[code_key]

        # Detect code changes and clear stale results
        previous_code = st.session_state.code_by_problem[code_key]
        if user_code != previous_code:
            st.session_state.code_by_problem[code_key] = user_code
            if problem["id"] in st.session_state.results_by_problem:
                del st.session_state.results_by_problem[problem["id"]]

        # Reset / info row
        reset_col, info_col = st.columns([1, 3])
        with reset_col:
            reset_clicked = st.button("🔄 Reset Code", use_container_width=True)
        with info_col:
            st.caption("Run Code checks visible tests. Submit checks all tests and saves your result.")

        if reset_clicked:
            st.session_state.code_by_problem[code_key] = problem["starter_code"]
            st.session_state.editor_versions[code_key] += 1
            if problem["id"] in st.session_state.results_by_problem:
                del st.session_state.results_by_problem[problem["id"]]
            if problem["id"] in st.session_state.tutor_answers_by_problem:
                del st.session_state.tutor_answers_by_problem[problem["id"]]
            if problem["id"] in st.session_state.last_run_code_by_problem:
                del st.session_state.last_run_code_by_problem[problem["id"]]
            st.rerun()

        # Stale-code warning
        last_run_code = st.session_state.last_run_code_by_problem.get(problem["id"])
        if last_run_code is not None and last_run_code != user_code:
            st.warning("⚠️ Code changed since the last run. Run again to update results.")

        # Run / Submit buttons
        run_col, submit_col = st.columns(2)
        with run_col:
            run_clicked = st.button(
                "▶ Run Code",
                use_container_width=True,
                help="Runs visible tests only. Does not save the submission."
            )
        with submit_col:
            submit_clicked = st.button(
                "🚀 Submit",
                use_container_width=True,
                help="Runs all tests (including hidden) and saves your submission."
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

        # ── Test Results ────────────────────────────────────────────────────────
        current_result = st.session_state.results_by_problem.get(problem["id"])

        if current_result:
            st.divider()
            result = current_result
            r_status = result.get("status", "error")

            if r_status == "passed":
                st.success("✅ **Accepted** — All tests passed!")
            elif r_status == "failed":
                st.error("❌ **Wrong Answer** — Some tests failed.")
            else:
                st.error(f"⚠️ **Runtime Error** — {result.get('message', 'Something went wrong.')}")

            if "error" in result:
                st.code(result["error"])

            test_results = result.get("results", [])
            if test_results:
                st.markdown(f"**Test Results** ({sum(1 for t in test_results if t['passed'])}/{len(test_results)} passed)")
                for test in test_results:
                    icon = "✅" if test["passed"] else "❌"
                    label = f"{icon} Test {test['test_number']} — {'Passed' if test['passed'] else 'Failed'}"
                    with st.expander(label, expanded=not test["passed"]):
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            st.markdown("**Input**")
                            st.json(test["input"])
                        with c2:
                            st.markdown("**Expected**")
                            st.json(test["expected"])
                        with c3:
                            st.markdown("**Actual**")
                            st.json(test["actual"])
                        if test.get("error"):
                            st.markdown("**Error**")
                            st.code(test["error"])

    # ── AI Tutor tab ────────────────────────────────────────────────────────────
    with tutor_tab:
        current_result = st.session_state.results_by_problem.get(problem["id"])
        first_failed_test = get_first_failed_test(current_result)

        st.markdown("**Ask the AI tutor for help with this problem.**")

        # Quick-action buttons
        btn_col1, btn_col2 = st.columns(2)
        btn_col3, btn_col4 = st.columns(2)

        with btn_col1:
            explain_clicked = st.button("📖 Explain Problem", use_container_width=True)
        with btn_col2:
            hint_clicked = st.button("💡 Give Hint", use_container_width=True)
        with btn_col3:
            review_clicked = st.button("🔍 Review My Code", use_container_width=True)
        with btn_col4:
            debug_clicked = st.button(
                "🐛 Debug Failed Test",
                use_container_width=True,
                disabled=first_failed_test is None,
                help="Run your code first. Available when a test fails."
            )

        if first_failed_test is None:
            st.caption("Run your code and fail a test to enable **Debug Failed Test**.")

        # Handle quick-action clicks
        if explain_clicked or hint_clicked or review_clicked or debug_clicked:
            failed_test_payload = None
            if explain_clicked:
                tutor_endpoint = "/tutor/explain-problem"
                answer_type = "Explain Problem"
            elif hint_clicked:
                tutor_endpoint = "/tutor/hint"
                answer_type = "Hint"
            elif review_clicked:
                tutor_endpoint = "/tutor/review-code"
                answer_type = "Review Code"
            else:
                tutor_endpoint = "/tutor/debug-failed-test"
                answer_type = "Debug Failed Test"
                failed_test_payload = first_failed_test

            with st.spinner("CodeTutor is thinking…"):
                answer = call_tutor(
                    endpoint=tutor_endpoint,
                    problem_id=problem["id"],
                    code=user_code,
                    failed_test=failed_test_payload
                )
                add_tutor_answer(
                    problem_id=problem["id"],
                    answer_type=answer_type,
                    answer=answer
                )

        st.divider()

        # Custom question
        st.markdown("**Ask a Custom Question**")
        custom_question = st.text_input(
            "Question",
            placeholder="Example: Why do we use a hash map here?",
            key=f"custom_question_{problem['id']}",
            label_visibility="collapsed"
        )
        ask_clicked = st.button(
            "Ask CodeTutor",
            use_container_width=True,
            disabled=not custom_question.strip()
        )

        if ask_clicked:
            with st.spinner("CodeTutor is thinking…"):
                answer = call_tutor(
                    endpoint="/tutor/ask",
                    problem_id=problem["id"],
                    code=user_code,
                    failed_test=first_failed_test,
                    question=custom_question
                )
                add_tutor_answer(
                    problem_id=problem["id"],
                    answer_type="Custom Question",
                    answer=answer,
                    question=custom_question
                )

        # Tutor history
        current_tutor_history = st.session_state.tutor_answers_by_problem.get(problem["id"], [])

        if current_tutor_history:
            st.divider()
            hist_col, clear_col = st.columns([3, 1])
            with hist_col:
                st.markdown("**AI Tutor History**")
            with clear_col:
                clear_history_clicked = st.button(
                    "🗑️ Clear",
                    use_container_width=True,
                    help="Clear tutor history for this problem"
                )

            if clear_history_clicked:
                st.session_state.tutor_answers_by_problem[problem["id"]] = []
                st.rerun()

            for index, entry in enumerate(current_tutor_history, start=1):
                title = f"{entry['type']} — {entry['created_at']}"
                with st.expander(title, expanded=(index == 1)):
                    if entry.get("question"):
                        st.markdown(f"**Q:** {entry['question']}")
                    st.write(entry["answer"])

    # ── Submissions tab ─────────────────────────────────────────────────────────
    with history_tab:
        st.markdown("**Latest submissions for this problem**")

        history = get_submission_history(problem["id"])

        if not history:
            st.info("No submissions yet for this problem. Submit your code to see results here.")
        else:
            latest = history[:5]

            # Build a display table
            rows = []
            for sub in latest:
                rows.append({
                    "Time": sub["created_at"],
                    "Status": status_label(sub["status"]),
                    "Tests": f"{sub['passed_tests']} / {sub['total_tests']}"
                })

            st.table(rows)

            st.caption(f"Showing latest {len(latest)} of {len(history)} submissions.")