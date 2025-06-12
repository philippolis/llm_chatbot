import streamlit as st

def init_session_state():
    """Initializes the session state variables."""
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("agent", None)
    st.session_state.setdefault("df", None)
    st.session_state.setdefault("data_source_locked", False)
    st.session_state.setdefault("include_visualisations", True)
    st.session_state.setdefault("simple_language", False)
    st.session_state.setdefault("accessibility_options_set", False)
    st.session_state.setdefault("show_csv_uploader", False)
    st.session_state.setdefault("data_source_name", "Titanic Dataset")

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4.1-nano" # Or your preferred model
    if "last_response_id" not in st.session_state: # Though this might not be used if messages are cleared
        st.session_state.last_response_id = None
    st.session_state.setdefault("simple_language", False)
    st.session_state.setdefault("accessibility_options_set", False)
    st.session_state.setdefault("show_csv_uploader", False)
    st.session_state.setdefault("data_source_name", "Titanic Dataset") 