# frontend/pages/register.py

import streamlit as st

from utils.session_state import initialize_session_state
from utils.api_client import register

initialize_session_state()

st.title("📝 Register")

st.info(
    "Create a new GradeOps account and choose your role. "
    "Instructors can create courses, exams, questions, and run grading. "
    "TAs can access only the features permitted by backend role-based access control."
)

email = st.text_input("Email")
password = st.text_input("Password", type="password")

role = st.selectbox(
    "Role",
    ["instructor", "ta"]
)

if st.button("🚀 Create Account", type="primary"):
    if not email.strip():
        st.warning("Please enter your email.")
    elif not password:
        st.warning("Please enter your password.")
    else:
        try:
            response = register(
                email=email,
                password=password,
                role=role
            )

            if response.status_code in [200, 201]:
                data = response.json()

                st.success("Account created successfully!")
                st.json(data)

                st.info(
                    "Your account has been created. "
                    "Proceed to the Login page to sign in."
                )

            else:
                st.error(
                    f"Registration failed "
                    f"({response.status_code}): "
                    f"{response.text}"
                )

        except Exception as e:
            st.error(f"Connection error: {e}")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔐 Go to Login"):
        st.switch_page("pages/login.py")

with col2:
    if st.button("🏠 Home"):
        st.switch_page("app.py")