# frontend/app.py

import streamlit as st
from utils.session_state import initialize_session_state

initialize_session_state()

st.set_page_config(
    page_title="GradeOps",
    page_icon="📝",
    layout="wide"
)

st.title("📝 GradeOps")
st.subheader("AI-Powered Automated Exam Grading Platform")

st.markdown("""
Welcome to GradeOps.

This platform automates the complete exam evaluation workflow:

1. Register as Instructor or TA
2. Log in securely
3. Create and manage courses
4. Create exams
5. Add questions, expected answers, and rubrics
6. Upload scanned answer sheets (PDF)
7. Run OCR to extract handwritten text
8. Grade the entire exam using AI
9. View OCR and grading results
""")

# --------------------------------------------------
# Authentication Status
# --------------------------------------------------
if st.session_state.token:
    st.success(
        f"Logged in as "
        f"{st.session_state.user_email} "
        f"({st.session_state.user_role})"
    )
else:
    st.info("You are not logged in.")

# --------------------------------------------------
# Navigation
# --------------------------------------------------
st.header("🧭 Navigation")

# Row 1
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📝 Register"):
        st.switch_page("pages/register.py")

with col2:
    if st.button("🔐 Login"):
        st.switch_page("pages/login.py")

with col3:
    if st.button("📊 Dashboard"):
        st.switch_page("pages/dashboard.py")

# Row 2
col4, col5, col6 = st.columns(3)

with col4:
    if st.button("📚 Courses"):
        st.switch_page("pages/courses.py")

with col5:
    if st.button("📝 Exams"):
        st.switch_page("pages/exams.py")

with col6:
    if st.button("❓ Questions"):
        st.switch_page("pages/questions.py")

# Row 3
col7, col8, col9 = st.columns(3)

with col7:
    if st.button("📤 Upload PDFs"):
        st.switch_page("pages/upload_pdf.py")

with col8:
    if st.button("🔍 Run OCR"):
        st.switch_page("pages/run_ocr.py")

with col9:
    if st.button("🤖 Grade Entire Exam"):
        st.switch_page("pages/grade_exam.py")

# Row 4
col10, col11 = st.columns(2)

with col10:
    if st.button("📈 Results"):
        st.switch_page("pages/results.py")

with col11:
    if st.button("🏠 Home"):
        st.rerun()

# --------------------------------------------------
# Current Session Context
# --------------------------------------------------
st.header("📌 Current Session Context")

st.write("User Email:", st.session_state.user_email)
st.write("User Role:", st.session_state.user_role)
st.write("User ID:", st.session_state.user_id)
st.write("Selected Course ID:", st.session_state.course_id)
st.write("Selected Exam ID:", st.session_state.exam_id)
st.write("Selected Answer Sheet ID:", st.session_state.answer_sheet_id)

# --------------------------------------------------
# Dashboard Preview
# --------------------------------------------------
st.header("📈 Monitoring Preview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Courses", "—")

with col2:
    st.metric("Exams", "—")

with col3:
    st.metric("Questions", "—")

with col4:
    st.metric("Answer Sheets", "—")

col5, col6, col7, col8 = st.columns(4)

with col5:
    st.metric("OCR Completed", "—")

with col6:
    st.metric("Exams Graded", "—")

with col7:
    st.metric("Human Review", "—")

with col8:
    st.metric("Plagiarism Flags", "—")

st.info("""
These metrics will be populated as your backend stores OCR results,
grading outcomes, verification flags, and plagiarism indicators.
""")

# --------------------------------------------------
# Logout
# --------------------------------------------------
if st.session_state.token:
    if st.button("🚪 Logout", type="primary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()