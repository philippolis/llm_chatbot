import streamlit as st

def init_session_state():
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4.1-nano" # Or your preferred model
    if 'data_source_locked' not in st.session_state:
        st.session_state.data_source_locked = False
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "last_response_id" not in st.session_state: # Though this might not be used if messages are cleared
        st.session_state.last_response_id = None 