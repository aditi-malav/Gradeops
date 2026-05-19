# Replace EVERYTHING in frontend/pages/results.py with this minimal version.
# This page ONLY shows the backend JSON exactly as returned.
# No tables, no OCR parsing, no score extraction, no summary metrics.

import streamlit as st
import requests

from utils.session_state import initialize_session_state

initialize_session_state()

BASE_URL = "http://localhost:8000"


def get_headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}"
    }


# ----------------------------------------------------------
# Page Setup
# ----------------------------------------------------------
st.set_page_config(
    page_title="Exam Results Review",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Exam Results Review")

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
# Load Results from Session
# ----------------------------------------------------------
grading_result = st.session_state.get("last_grading_result")

# ----------------------------------------------------------
# Fallback: Try Loading from Backend Using Exam ID
# ----------------------------------------------------------
if not grading_result:
    exam_id = st.session_state.get("exam_id")

    if exam_id:
        try:
            response = requests.get(
                f"{BASE_URL}/grading/results/{exam_id}",
                headers=get_headers(),
                timeout=30
            )

            if response.status_code == 200:
                grading_result = response.json()
                st.session_state.last_grading_result = grading_result

        except Exception:
            pass

# ----------------------------------------------------------
# No Data Found
# ----------------------------------------------------------
if not grading_result:
    st.info(
        "No grading results found in session or backend."
    )

    if st.button("🤖 Go to Grade Exam"):
        st.switch_page("pages/grade_exam.py")

    st.stop()

# ----------------------------------------------------------
# Display Raw JSON Only
# ----------------------------------------------------------
st.header("🔍 Raw Backend JSON")

# Shows the JSON in a clean expandable tree format
st.json(grading_result)

# ----------------------------------------------------------
# Navigation
# ----------------------------------------------------------
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🤖 Grade Entire Exam", use_container_width=True):
        st.switch_page("pages/grade_exam.py")

with col2:
    if st.button("📊 Dashboard", use_container_width=True):
        st.switch_page("pages/dashboard.py")

with col3:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")