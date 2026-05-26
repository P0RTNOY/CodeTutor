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


st.title("CodeTutor")
st.write("Practice coding problems with an AI tutor.")


problems = get_problems()

if not problems:
    st.warning("No problems found.")
    st.stop()


problem_titles = {
    problem["title"]: problem["id"]
    for problem in problems
}

selected_title = st.sidebar.selectbox(
    "Choose a problem",
    list(problem_titles.keys())
)

selected_problem_id = problem_titles[selected_title]
problem = get_problem(selected_problem_id)

if problem is None:
    st.stop()


left_col, right_col = st.columns([1, 1])


with left_col:
    st.header(problem["title"])

    st.write(f"**Difficulty:** {problem['difficulty']}")
    st.write(f"**Tags:** {', '.join(problem['tags'])}")

    st.subheader("Description")
    st.write(problem["description"])

    st.subheader("Examples")

    for index, example in enumerate(problem["examples"], start=1):
        st.markdown(f"**Example {index}**")
        st.code(f"Input: {example['input']}\nOutput: {example['output']}")

        if "explanation" in example:
            st.write(f"Explanation: {example['explanation']}")


with right_col:
    st.subheader("Your Python Solution")

    user_code = st.text_area(
        label="Code",
        value=problem["starter_code"],
        height=400
    )

    col_run, col_submit = st.columns(2)

    with col_run:
        run_clicked = st.button("Run Code")

    with col_submit:
        submit_clicked = st.button("Submit")

    if run_clicked or submit_clicked:
        endpoint = "/submit" if submit_clicked else "/run"

        try:
            response = requests.post(
                f"{API_BASE_URL}{endpoint}",
                json={
                    "problem_id": problem["id"],
                    "code": user_code
                },
                timeout=10
            )

            response.raise_for_status()
            result = response.json()

            if result["status"] == "passed":
                st.success("All tests passed!")
            elif result["status"] == "failed":
                st.error("Some tests failed.")
            else:
                st.error(result.get("message", "Something went wrong."))

            if "error" in result:
                st.code(result["error"])

            for test_result in result.get("results", []):
                st.markdown(f"### Test {test_result['test_number']}")

                if test_result["passed"]:
                    st.success("Passed")
                else:
                    st.error("Failed")

                st.write("Input:")
                st.json(test_result["input"])

                st.write("Expected:")
                st.json(test_result["expected"])

                st.write("Actual:")
                st.json(test_result["actual"])

                if test_result["error"]:
                    st.write("Error:")
                    st.code(test_result["error"])

        except requests.exceptions.RequestException as error:
            st.error(f"Could not run code: {error}")
        st.divider()
    st.subheader("AI Tutor")

    tutor_col1, tutor_col2, tutor_col3 = st.columns(3)

    with tutor_col1:
        explain_clicked = st.button("Explain Problem")

    with tutor_col2:
        hint_clicked = st.button("Give Hint")

    with tutor_col3:
        review_clicked = st.button("Review My Code")

    if explain_clicked or hint_clicked or review_clicked:
        if explain_clicked:
            tutor_endpoint = "/tutor/explain-problem"
        elif hint_clicked:
            tutor_endpoint = "/tutor/hint"
        else:
            tutor_endpoint = "/tutor/review-code"

        with st.spinner("CodeTutor is thinking..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}{tutor_endpoint}",
                    json={
                        "problem_id": problem["id"],
                        "code": user_code
                    },
                    timeout=130
                )

                response.raise_for_status()
                tutor_result = response.json()

                st.markdown("### Tutor Response")
                st.write(tutor_result["answer"])

            except requests.exceptions.RequestException as error:
                st.error(f"Could not contact AI tutor: {error}")
        