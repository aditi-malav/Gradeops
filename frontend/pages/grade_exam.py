# frontend/pages/grade_exam.py

import requests
import streamlit as st

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
    page_title="Grade Entire Exam",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Grade Entire Exam")

# ----------------------------------------------------------
# Authentication Check
# ----------------------------------------------------------
if not st.session_state.token:
    st.warning("Please log in first.")
    st.stop()

# ----------------------------------------------------------
# Role Check
# ----------------------------------------------------------
if st.session_state.user_role != "instructor":
    st.error("Only instructors can run automated grading.")

    if st.button("📈 Open Results", use_container_width=True):
        st.switch_page("pages/results.py")

    st.stop()

# ----------------------------------------------------------
# Header Information
# ----------------------------------------------------------
st.success(
    f"Logged in as "
    f"{st.session_state.user_email} "
    f"({st.session_state.user_role})"
)

st.info(
    "This will process all uploaded answer sheets for the "
    "selected Exam ID and perform OCR verification, "
    "AI rubric-based grading, plagiarism detection, "
    "and human review flagging."
)

# ----------------------------------------------------------
# Exam Selection
# ----------------------------------------------------------
default_exam_id = (
    int(st.session_state.exam_id)
    if st.session_state.exam_id
    else 1
)

exam_id = st.number_input(
    "Exam ID",
    min_value=1,
    value=default_exam_id,
    step=1
)

st.session_state.exam_id = exam_id

# ----------------------------------------------------------
# Existing Session Status
# ----------------------------------------------------------
if st.session_state.get("last_grading_result"):
    st.info(
        "A grading result is already loaded in this session. "
        "Running grading again will replace it."
    )

# ----------------------------------------------------------
# Grade Entire Exam
# ----------------------------------------------------------
if st.button(
    "🚀 Grade Entire Exam",
    type="primary",
    use_container_width=True
):
    with st.spinner(
        "Running OCR verification, rubric-based scoring, "
        "generating justifications, and checking plagiarism..."
    ):
        try:
            response = requests.post(
                f"{BASE_URL}/grading/grade-exam/{exam_id}",
                headers=get_headers(),
                timeout=300
            )

            # --------------------------------------------------
            # Success
            # --------------------------------------------------
            if response.status_code in [200, 201]:
                result = response.json()

                # Store full backend response
                st.session_state.last_grading_result = result
                st.session_state.grading_complete = True
                st.session_state.selected_submission = None
                st.session_state.answer_sheet_id = None
                st.session_state.exam_id = exam_id

                st.success("✅ Exam graded successfully!")

                # Show backend message if present
                if (
                    isinstance(result, dict)
                    and result.get("message")
                ):
                    st.info(result["message"])

                # Show exact backend JSON
                st.markdown("---")
                st.header("🔍 Raw Backend JSON")
                st.json(result)

                # Automatically open results page
                st.switch_page("pages/results.py")

            # --------------------------------------------------
            # Backend Error
            # --------------------------------------------------
            else:
                st.error(
                    f"Backend Error {response.status_code}"
                )

                try:
                    st.json(response.json())
                except Exception:
                    st.code(response.text)

        # ------------------------------------------------------
        # Connection Error
        # ------------------------------------------------------
        except Exception as e:
            st.error(f"Connection error: {e}")

# ----------------------------------------------------------
# Navigation
# ----------------------------------------------------------
st.markdown("---")
st.header("🧭 Navigation")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button(
        "📤 Upload Answer Sheets",
        use_container_width=True
    ):
        st.switch_page("pages/upload_pdf.py")

with col2:
    if st.button(
        "📈 Results",
        use_container_width=True
    ):
        st.switch_page("pages/results.py")

with col3:
    if st.button(
        "📊 Dashboard",
        use_container_width=True
    ):
        st.switch_page("pages/dashboard.py")