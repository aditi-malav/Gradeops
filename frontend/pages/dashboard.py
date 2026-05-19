# frontend/pages/dashboard.py

import streamlit as st
import requests

from utils.session_state import initialize_session_state

initialize_session_state()

BASE_URL = "http://localhost:8000"


def get_headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}"
    }


def safe_get(url):
    try:
        response = requests.get(
            url,
            headers=get_headers(),
            timeout=15
        )

        if response.status_code == 200:
            return response.json()

    except Exception:
        pass

    return None


# ----------------------------------------------------------
# Page Setup
# ----------------------------------------------------------
st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 GradeOps Dashboard")

# ----------------------------------------------------------
# Authentication
# ----------------------------------------------------------
if not st.session_state.token:
    st.warning("Please log in first.")
    st.stop()

st.success(
    f"Logged in as "
    f"{st.session_state.user_email} "
    f"({st.session_state.user_role})"
)

# ----------------------------------------------------------
# Exam Context
# ----------------------------------------------------------
st.markdown("---")
st.header("📌 Current Exam Context")

exam_id = st.number_input(
    "Selected Exam ID",
    min_value=1,
    value=(
        int(st.session_state.exam_id)
        if st.session_state.exam_id
        else 1
    ),
    step=1
)

st.session_state.exam_id = exam_id

if st.session_state.get("last_grading_result"):
    st.success("Grading results are loaded in session.")
else:
    st.info("No grading results currently loaded.")

# ----------------------------------------------------------
# Session Information
# ----------------------------------------------------------
st.markdown("---")
st.header("👤 Session Information")

col1, col2, col3 = st.columns(3)

with col1:
    st.write("**User Email:**", st.session_state.user_email)

with col2:
    st.write("**Role:**", st.session_state.user_role)

with col3:
    st.write("**Exam ID:**", st.session_state.exam_id)

# ----------------------------------------------------------
# Instructor Dashboard
# ----------------------------------------------------------
if st.session_state.user_role == "instructor":
    st.markdown("---")
    st.header("👨‍🏫 Instructor Controls")

    row1 = st.columns(3)

    with row1[0]:
        if st.button("📚 Courses", use_container_width=True):
            st.switch_page("pages/courses.py")

    with row1[1]:
        if st.button("📝 Exams", use_container_width=True):
            st.switch_page("pages/exams.py")

    with row1[2]:
        if st.button("❓ Questions", use_container_width=True):
            st.switch_page("pages/questions.py")

    row2 = st.columns(3)

    with row2[0]:
        if st.button("📤 Upload PDFs", use_container_width=True):
            st.switch_page("pages/upload_pdf.py")

    with row2[1]:
        if st.button("🔍 Run OCR", use_container_width=True):
            st.switch_page("pages/run_ocr.py")

    with row2[2]:
        if st.button("🤖 Grade Entire Exam", use_container_width=True):
            st.switch_page("pages/grade_exam.py")

    row3 = st.columns(2)

    with row3[0]:
        if st.button("📈 View Results (JSON)", use_container_width=True):
            st.switch_page("pages/results.py")

    with row3[1]:
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("app.py")

# ----------------------------------------------------------
# TA Dashboard
# ----------------------------------------------------------
else:
    st.markdown("---")
    st.header("🧑‍🏫 TA Review Dashboard")

    st.info(
        "Teaching Assistants can review the exact backend "
        "grading JSON, including scores, plagiarism flags, "
        "and question-wise AI evaluations."
    )

    row = st.columns(2)

    with row[0]:
        if st.button("📈 View Results (JSON)", use_container_width=True):
            st.switch_page("pages/results.py")

    with row[1]:
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("app.py")

# ----------------------------------------------------------
# Preview Loaded JSON
# ----------------------------------------------------------
if st.session_state.get("last_grading_result"):
    st.markdown("---")

    with st.expander("🔍 Loaded Grading JSON Preview"):
        st.json(st.session_state.last_grading_result)

# ----------------------------------------------------------
# Logout
# ----------------------------------------------------------
st.markdown("---")

if st.button("🚪 Logout", type="primary"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    st.rerun()