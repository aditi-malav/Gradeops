# frontend/pages/exams.py

import streamlit as st
import requests

from utils.session_state import initialize_session_state

initialize_session_state()

BASE_URL = "http://localhost:8000"

st.title("📝 Exam Management")

if not st.session_state.token:
    st.warning("Please log in first.")
    st.stop()

if st.session_state.user_role != "instructor":
    st.error("Only instructors can create and manage exams.")
    st.stop()

default_course_id = (
    st.session_state.course_id
    if st.session_state.course_id
    else 1
)

st.info(
    "Create a new exam inside an existing course, "
    "or load and select previously created exams."
)

course_id = st.number_input(
    "Course ID",
    min_value=1,
    value=default_course_id,
    step=1
)

st.session_state.course_id = course_id

st.subheader("➕ Create New Exam")

title = st.text_input("Exam Title")

total_marks = st.number_input(
    "Total Marks",
    min_value=1,
    value=100,
    step=1
)

if st.button("💾 Create Exam", type="primary"):
    if not title.strip():
        st.warning("Please enter an exam title.")
    else:
        try:
            response = requests.post(
                f"{BASE_URL}/exams",
                json={
                    "course_id": int(course_id),
                    "title": title,
                    "total_marks": int(total_marks)
                },
                headers={
                    "Authorization":
                        f"Bearer {st.session_state.token}"
                }
            )

            if response.status_code in [200, 201]:
                data = response.json()

                st.success("Exam created successfully!")
                st.json(data)

                # Your backend returns:
                # {
                #   "message": "...",
                #   "exam": {
                #       "course_id": ...,
                #       "title": ...,
                #       "total_marks": ...
                #   }
                # }
                #
                # It does NOT return exam_id.
                # Therefore we instruct the user to load exams
                # and select the newly created one.
                st.info(
                    "Exam created. Click 'Load Existing Exams' "
                    "below and select the new exam to store "
                    "its Exam ID in the session."
                )

            else:
                st.error(
                    f"Error {response.status_code}: "
                    f"{response.text}"
                )

        except Exception as e:
            st.error(f"Connection error: {e}")

st.markdown("---")
st.subheader("📋 Existing Exams")

if st.button("🔄 Load Existing Exams"):
    try:
        response = requests.get(
            f"{BASE_URL}/courses/{course_id}/exams",
            headers={
                "Authorization":
                    f"Bearer {st.session_state.token}"
            }
        )

        if response.status_code == 200:
            data = response.json()
            exams = data.get("exams", [])

            if exams:
                for exam in exams:
                    with st.expander(
                        f"ID {exam['id']} | "
                        f"{exam['title']} | "
                        f"{exam['total_marks']} marks"
                    ):
                        st.write("Exam ID:", exam["id"])
                        st.write("Course ID:", exam["course_id"])
                        st.write("Created At:", exam["created_at"])

                        if st.button(
                            f"Select Exam {exam['id']}",
                            key=f"select_exam_{exam['id']}"
                        ):
                            st.session_state.exam_id = exam["id"]
                            st.success(
                                f"Selected Exam ID: "
                                f"{exam['id']}"
                            )
                            st.rerun()
            else:
                st.info("No exams found for this course.")

        else:
            st.error(
                f"Error {response.status_code}: "
                f"{response.text}"
            )

    except Exception as e:
        st.error(f"Connection error: {e}")

if st.session_state.exam_id:
    st.success(
        f"Current Selected Exam ID: "
        f"{st.session_state.exam_id}"
    )

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("❓ Questions"):
        st.switch_page("pages/questions.py")

with col2:
    if st.button("📤 Upload Answer Sheets"):
        st.switch_page("pages/upload_pdf.py")

with col3:
    if st.button("📊 Dashboard"):
        st.switch_page("pages/dashboard.py")