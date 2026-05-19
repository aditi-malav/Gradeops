# frontend/pages/questions.py

import streamlit as st
import requests

from utils.session_state import initialize_session_state

initialize_session_state()

BASE_URL = "http://localhost:8000"

st.title("❓ Questions and Rubrics")

if not st.session_state.token:
    st.warning("Please log in first.")
    st.stop()

if st.session_state.user_role != "instructor":
    st.error("Only instructors can create and manage questions.")
    st.stop()

default_exam_id = (
    st.session_state.exam_id
    if st.session_state.exam_id
    else 1
)

st.info(
    "Add questions, expected answers, and rubrics to an exam, "
    "or load previously created questions."
)

# --------------------------------------------------
# Select Exam
# --------------------------------------------------
exam_id = st.number_input(
    "Exam ID",
    min_value=1,
    value=default_exam_id,
    step=1
)

st.session_state.exam_id = exam_id

# --------------------------------------------------
# Create New Question
# --------------------------------------------------
st.subheader("➕ Add New Question")

question_number = st.number_input(
    "Question Number",
    min_value=1,
    step=1
)

max_marks = st.number_input(
    "Maximum Marks",
    min_value=1,
    step=1
)

expected_answer = st.text_area(
    "Expected Answer",
    height=150
)

rubric = st.text_area(
    "Rubric",
    height=200
)

if st.button("💾 Save Question", type="primary"):
    if not expected_answer.strip():
        st.warning("Please enter the expected answer.")
    elif not rubric.strip():
        st.warning("Please enter the rubric.")
    else:
        try:
            response = requests.post(
                f"{BASE_URL}/questions",
                json={
                    "exam_id": int(exam_id),
                    "question_number": int(question_number),
                    "max_marks": int(max_marks),
                    "expected_answer": expected_answer,
                    "rubric": rubric
                },
                headers={
                    "Authorization":
                        f"Bearer {st.session_state.token}"
                }
            )

            if response.status_code in [200, 201]:
                data = response.json()

                st.success("Question created successfully!")
                st.json(data)

            else:
                st.error(
                    f"Error {response.status_code}: "
                    f"{response.text}"
                )

        except Exception as e:
            st.error(f"Connection error: {e}")

# --------------------------------------------------
# Load Existing Questions
# --------------------------------------------------
st.markdown("---")
st.subheader("📋 Existing Questions")

if st.button("🔄 Load Existing Questions"):
    try:
        response = requests.get(
            f"{BASE_URL}/exams/{exam_id}/questions",
            headers={
                "Authorization":
                    f"Bearer {st.session_state.token}"
            }
        )

        if response.status_code == 200:
            data = response.json()
            questions = data.get("questions", [])

            if questions:
                for question in questions:
                    label = (
                        f"Q{question['question_number']} | "
                        f"{question['max_marks']} marks"
                    )

                    with st.expander(label):
                        st.write("Question ID:", question["id"])
                        st.write(
                            "Question Number:",
                            question["question_number"]
                        )
                        st.write(
                            "Maximum Marks:",
                            question["max_marks"]
                        )

                        st.subheader("Expected Answer")
                        st.write(
                            question["expected_answer"]
                        )

                        st.subheader("Rubric")
                        st.write(
                            question["rubric"]
                        )
            else:
                st.info("No questions found for this exam.")

        else:
            st.error(
                f"Error {response.status_code}: "
                f"{response.text}"
            )

    except Exception as e:
        st.error(f"Connection error: {e}")

# --------------------------------------------------
# Current Selected Exam
# --------------------------------------------------
if st.session_state.exam_id:
    st.success(
        f"Current Selected Exam ID: "
        f"{st.session_state.exam_id}"
    )

# --------------------------------------------------
# Navigation
# --------------------------------------------------
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📤 Upload Answer Sheets"):
        st.switch_page("pages/upload_pdf.py")

with col2:
    if st.button("📝 Exams"):
        st.switch_page("pages/exams.py")

with col3:
    if st.button("📊 Dashboard"):
        st.switch_page("pages/dashboard.py")