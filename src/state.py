import streamlit as st

def init_session_state():
    """Initializes the session state for the chatbot."""
    
    # --- Basic App State ---
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent" not in st.session_state:
        st.session_state.agent = None
    if "df" not in st.session_state:
        st.session_state.df = None

    # --- Configuration State ---
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4.1-nano"
    if "data_source_locked" not in st.session_state:
        st.session_state.data_source_locked = False
        
    # --- Accessibility Options ---
    if "include_visualisations" not in st.session_state:
        st.session_state.include_visualisations = False
    if "simple_language" not in st.session_state:
        st.session_state.simple_language = False
    if "show_code" not in st.session_state:
        st.session_state.show_code = True

    # --- UI State ---
    if 'show_csv_uploader' not in st.session_state:
        st.session_state.show_csv_uploader = False
    if 'data_source_name' not in st.session_state:
        st.session_state.data_source_name = "Titanic-Datensatz"

    if "agent_settings" not in st.session_state:
        st.session_state.agent_settings = {} 