# frontend/pages/run_ocr.py

import streamlit as st
import requests

from utils.session_state import initialize_session_state

initialize_session_state()

BASE_URL = "http://localhost:8000"

st.title("🔍 Run OCR")

if not st.session_state.token:
    st.warning("Please log in first.")
    st.stop()

if st.session_state.user_role != "instructor":
    st.error("Only instructors can run OCR.")
    st.stop()

default_answer_sheet_id = (
    st.session_state.answer_sheet_id
    if st.session_state.answer_sheet_id
    else 1
)

st.info(
    "Enter an existing Answer Sheet ID to run OCR and "
    "view the extracted handwritten text."
)

answer_sheet_id = st.number_input(
    "Answer Sheet ID",
    min_value=1,
    value=default_answer_sheet_id,
    step=1
)

st.session_state.answer_sheet_id = answer_sheet_id

if st.session_state.answer_sheet_id:
    st.success(
        f"Current Selected Answer Sheet ID: "
        f"{st.session_state.answer_sheet_id}"
    )

# --------------------------------------------------
# Run OCR
# --------------------------------------------------
if st.button("🚀 Run OCR", type="primary"):
    with st.spinner("Extracting handwritten text..."):
        try:
            response = requests.post(
                f"{BASE_URL}/answer-sheets/{answer_sheet_id}/run-ocr",
                headers={
                    "Authorization":
                        f"Bearer {st.session_state.token}"
                }
            )

            if response.status_code in [200, 201]:
                data = response.json()

                st.success("OCR completed successfully!")
                st.json(data)

            else:
                st.error(
                    f"Error {response.status_code}: "
                    f"{response.text}"
                )

        except Exception as e:
            st.error(f"Connection error: {e}")

# --------------------------------------------------
# View OCR Result
# --------------------------------------------------
st.markdown("---")
st.subheader("📄 View OCR Result")

if st.button("🔄 Load OCR Result"):
    try:
        response = requests.get(
            f"{BASE_URL}/answer-sheets/{answer_sheet_id}/ocr",
            headers={
                "Authorization":
                    f"Bearer {st.session_state.token}"
            }
        )

        if response.status_code == 200:
            data = response.json()

            st.success("OCR result loaded successfully!")

            st.write("Provider:", data.get("ocr_provider"))
            st.write("Status:", data.get("processing_status"))
            st.write("Created At:", data.get("created_at"))

            st.text_area(
                "Extracted Text",
                value=data.get("extracted_text", ""),
                height=400
            )

        else:
            st.error(
                f"Error {response.status_code}: "
                f"{response.text}"
            )

    except Exception as e:
        st.error(f"Connection error: {e}")

# --------------------------------------------------
# Navigation
# --------------------------------------------------
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📤 Upload Answer Sheets"):
        st.switch_page("pages/upload_pdf.py")

with col2:
    if st.button("🤖 Grade Entire Exam"):
        st.switch_page("pages/grade_exam.py")

with col3:
    if st.button("📊 Dashboard"):
        st.switch_page("pages/dashboard.py")