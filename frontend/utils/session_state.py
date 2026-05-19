# frontend/utils/session_state.py

import streamlit as st


def initialize_session_state():
    defaults = {
        # --------------------------------------------------
        # Authentication
        # --------------------------------------------------
        "token": None,
        "user_email": None,
        "user_role": None,
        "user_id": None,

        # --------------------------------------------------
        # Selected Entities
        # --------------------------------------------------
        "course_id": None,
        "exam_id": None,
        "answer_sheet_id": None,

        # --------------------------------------------------
        # Workflow State
        # --------------------------------------------------
        "grading_complete": False,

        # Complete backend response from:
        # POST /grading/grade-exam/{exam_id}
        # This stores the exact JSON returned by the backend.
        "last_grading_result": None,

        # Currently selected submission in the UI
        "selected_submission": None,

        # Navigation flag (optional)
        "open_results_after_grading": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value