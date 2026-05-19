# frontend/pages/upload_pdf.py

import streamlit as st
import requests

from utils.session_state import initialize_session_state

initialize_session_state()

BASE_URL = "http://localhost:8000"

st.title("📤 Upload Answer Sheets")

if not st.session_state.token:
    st.warning("Please log in first.")
    st.stop()

if st.session_state.user_role != "instructor":
    st.error("Only instructors can upload answer sheets.")
    st.stop()

default_exam_id = (
    st.session_state.exam_id
    if st.session_state.exam_id
    else 1
)

st.info(
    "Upload scanned answer sheets in PDF format, or load "
    "previously uploaded answer sheets for an existing exam."
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

if st.session_state.exam_id:
    st.success(
        f"Current Selected Exam ID: "
        f"{st.session_state.exam_id}"
    )

# --------------------------------------------------
# Existing Answer Sheets
# --------------------------------------------------
st.markdown("---")
st.subheader("📋 Existing Answer Sheets")

if st.button("🔄 Load Existing Answer Sheets"):
    try:
        response = requests.get(
            f"{BASE_URL}/exams/{exam_id}/answer-sheets",
            headers={
                "Authorization":
                    f"Bearer {st.session_state.token}"
            }
        )

        if response.status_code == 200:
            data = response.json()
            answer_sheets = data.get("answer_sheets", [])

            if answer_sheets:
                for sheet in answer_sheets:
                    sheet_id = sheet.get("id")

                    label = f"Answer Sheet ID {sheet_id}"

                    if sheet.get("file_name"):
                        label += f" | {sheet['file_name']}"

                    with st.expander(label):
                        st.write(
                            "Answer Sheet ID:",
                            sheet.get("id")
                        )

                        if sheet.get("exam_id") is not None:
                            st.write(
                                "Exam ID:",
                                sheet.get("exam_id")
                            )

                        if sheet.get("student_name"):
                            st.write(
                                "Student Name:",
                                sheet.get("student_name")
                            )

                        if sheet.get("roll_number"):
                            st.write(
                                "Roll Number:",
                                sheet.get("roll_number")
                            )

                        if sheet.get("created_at"):
                            st.write(
                                "Created At:",
                                sheet.get("created_at")
                            )

                        if st.button(
                            f"Select Answer Sheet {sheet_id}",
                            key=f"select_sheet_{sheet_id}"
                        ):
                            st.session_state.answer_sheet_id = (
                                sheet_id
                            )
                            st.success(
                                f"Selected Answer Sheet ID: "
                                f"{sheet_id}"
                            )
                            st.rerun()
            else:
                st.info(
                    "No answer sheets found for this exam."
                )

        else:
            st.error(
                f"Error {response.status_code}: "
                f"{response.text}"
            )

    except Exception as e:
        st.error(f"Connection error: {e}")

# --------------------------------------------------
# Upload New PDF
# --------------------------------------------------
st.markdown("---")
st.subheader("📄 Upload New Answer Sheet")

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"]
)

if uploaded_file and st.button("🚀 Upload PDF", type="primary"):
    with st.spinner("Uploading answer sheet..."):
        try:
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "application/pdf"
                )
            }

            # Backend expects exam_id as a query parameter:
            # /upload-answer-sheets?exam_id=<id>
            response = requests.post(
                f"{BASE_URL}/upload-answer-sheets?exam_id={exam_id}",
                files=files,
                headers={
                    "Authorization":
                        f"Bearer {st.session_state.token}"
                }
            )

            if response.status_code in [200, 201]:
                result = response.json()

                st.success("PDF uploaded successfully!")
                st.json(result)

                # Save answer_sheet_id if returned
                if "answer_sheet" in result:
                    answer_sheet = result["answer_sheet"]

                    if (
                        isinstance(answer_sheet, dict)
                        and "id" in answer_sheet
                    ):
                        st.session_state.answer_sheet_id = (
                            answer_sheet["id"]
                        )

                elif "answer_sheet_id" in result:
                    st.session_state.answer_sheet_id = (
                        result["answer_sheet_id"]
                    )

                elif "id" in result:
                    st.session_state.answer_sheet_id = (
                        result["id"]
                    )

                if st.session_state.answer_sheet_id:
                    st.success(
                        "Stored Answer Sheet ID: "
                        f"{st.session_state.answer_sheet_id}"
                    )

            else:
                st.error(
                    f"Error {response.status_code}: "
                    f"{response.text}"
                )

        except Exception as e:
            st.error(f"Connection error: {e}")

# --------------------------------------------------
# Current Selected Answer Sheet
# --------------------------------------------------
if st.session_state.answer_sheet_id:
    st.info(
        f"Selected Answer Sheet ID: "
        f"{st.session_state.answer_sheet_id}"
    )

# --------------------------------------------------
# Navigation
# --------------------------------------------------
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔍 Run OCR"):
        st.switch_page("pages/run_ocr.py")

with col2:
    if st.button("🤖 Grade Entire Exam"):
        st.switch_page("pages/grade_exam.py")

with col3:
    if st.button("📊 Dashboard"):
        st.switch_page("pages/dashboard.py")