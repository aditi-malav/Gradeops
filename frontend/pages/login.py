# frontend/pages/login.py

import streamlit as st

from utils.session_state import initialize_session_state
from utils.api_client import login, get_current_user

initialize_session_state()

st.title("🔐 Login")

st.info(
    "Log in using an existing account. "
    "Accounts created earlier through Swagger are also supported."
)

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("🚀 Login", type="primary"):
    if not email.strip():
        st.warning("Please enter your email.")
    elif not password:
        st.warning("Please enter your password.")
    else:
        try:
            # Step 1: Login and get JWT token
            response = login(email, password)

            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")

                if not token:
                    st.error("Login succeeded but no access token was returned.")
                    st.stop()

                # Store token immediately
                st.session_state.token = token

                # Step 2: Fetch user details from /me
                me_response = get_current_user(token)

                if me_response.status_code == 200:
                    me = me_response.json()

                    st.session_state.user_email = me.get("email")
                    st.session_state.user_role = me.get("role")
                    st.session_state.user_id = me.get("user_id")

                else:
                    st.error(
                        f"Failed to fetch user details: "
                        f"{me_response.text}"
                    )
                    st.stop()

                st.success("Login successful!")
                st.switch_page("pages/dashboard.py")

            else:
                st.error(
                    f"Login failed ({response.status_code}): "
                    f"{response.text}"
                )

        except Exception as e:
            st.error(f"Connection error: {e}")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    if st.button("📝 Register New Account"):
        st.switch_page("pages/register.py")

with col2:
    if st.button("🏠 Home"):
        st.switch_page("app.py")