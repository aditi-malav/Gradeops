# frontend/pages/courses.py

import streamlit as st
from utils.session_state import initialize_session_state
from utils.api_client import create_course, get_courses

initialize_session_state()

st.title("📚 Course Management")

# Ensure user is logged in
if not st.session_state.token:
    st.warning("Please log in first.")
    st.stop()

# Only instructors can create courses
if st.session_state.user_role != "instructor":
    st.error("Only instructors can create and manage courses.")
    st.stop()

st.info(
    "Create a new course or load previously created courses "
    "(including those created earlier through Swagger)."
)

# --------------------------------------------------
# Create New Course
# --------------------------------------------------
st.subheader("➕ Create New Course")

course_name = st.text_input("Course Name")
course_code = st.text_input("Course Code")

if st.button("💾 Create Course", type="primary"):
    if not course_name.strip():
        st.warning("Please enter a course name.")
    elif not course_code.strip():
        st.warning("Please enter a course code.")
    else:
        try:
            response = create_course(
                name=course_name,
                code=course_code,
                token=st.session_state.token
            )

            if response.status_code in [200, 201]:
                data = response.json()

                st.success("Course created successfully!")
                st.json(data)

                # Save course_id if present in response
                if "course" in data and "id" in data["course"]:
                    st.session_state.course_id = data["course"]["id"]
                elif "id" in data:
                    st.session_state.course_id = data["id"]

            else:
                st.error(
                    f"Error {response.status_code}: "
                    f"{response.text}"
                )

        except Exception as e:
            st.error(f"Connection error: {e}")

# --------------------------------------------------
# Load Existing Courses
# --------------------------------------------------
st.markdown("---")
st.subheader("📋 Existing Courses")

if st.button("🔄 Load Courses"):
    try:
        response = get_courses(st.session_state.token)

        if response.status_code == 200:
            data = response.json()

            # Support both:
            # {"courses": [...]} and [...]
            if isinstance(data, dict):
                courses = data.get("courses", [])
            else:
                courses = data

            if courses:
                for course in courses:
                    course_id = course.get("id")
                    course_name = course.get("name", "Unnamed Course")
                    course_code = course.get("code", "")

                    with st.expander(
                        f"ID {course_id} | "
                        f"{course_name} "
                        f"({course_code})"
                    ):
                        st.write("Course ID:", course_id)
                        st.write("Name:", course_name)
                        st.write("Code:", course_code)

                        if st.button(
                            f"Select Course {course_id}",
                            key=f"select_course_{course_id}"
                        ):
                            st.session_state.course_id = course_id
                            st.success(
                                f"Selected Course ID: {course_id}"
                            )

            else:
                st.info("No courses found.")

        else:
            st.error(
                f"Error {response.status_code}: "
                f"{response.text}"
            )

    except Exception as e:
        st.error(f"Connection error: {e}")

# --------------------------------------------------
# Current Selected Course
# --------------------------------------------------
if st.session_state.course_id:
    st.success(
        f"Current Selected Course ID: "
        f"{st.session_state.course_id}"
    )

# --------------------------------------------------
# Navigation
# --------------------------------------------------
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📝 Exams"):
        st.switch_page("pages/exams.py")

with col2:
    if st.button("📊 Dashboard"):
        st.switch_page("pages/dashboard.py")

with col3:
    if st.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()