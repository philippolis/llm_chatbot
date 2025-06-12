import streamlit as st
import pandas as pd
from src.agent import create_agent

def recreate_agent():
    """Re-creates the agent with the latest accessibility settings."""
    if st.session_state.df is not None:
        st.session_state.agent = create_agent(
            st.session_state.df,
            include_visualisations=st.session_state.include_visualisations,
            simple_language=st.session_state.simple_language
        )

def display_setup_expander():
    # The expander will now be open by default.
    with st.expander("⚙️ Settings and Data Source", expanded=True):
        st.header("Accessibility Options")
        st.toggle(
            "Include visualisations in answers?", 
            key="include_visualisations",
            on_change=recreate_agent
        )
        st.toggle(
            "Use simple language?", 
            key="simple_language",
            on_change=recreate_agent
        )

        st.header("Data Source")
        
        if not st.session_state.show_csv_uploader:
            st.info(f"Currently using: **{st.session_state.data_source_name}**.")
            if st.button("Change dataset"):
                st.session_state.show_csv_uploader = True
                st.rerun()
        else:
            with st.form("data_source_form"):
                uploaded_file_value = st.file_uploader(
                    "Upload your CSV file", 
                    type="csv", 
                    key="csv_uploader"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("Load CSV and Re-initialize")
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state.show_csv_uploader = False
                        st.rerun()

                if submitted:
                    if uploaded_file_value is not None:
                        try:
                            current_df = pd.read_csv(uploaded_file_value)
                            st.session_state.df = current_df
                            st.session_state.data_source_name = uploaded_file_value.name
                            
                            # Agent is now re-created on toggle change, but we still need to create it
                            # when a new file is loaded.
                            recreate_agent() 
                            
                            st.session_state.data_source_locked = True
                            st.session_state.messages = []
                            st.session_state.show_csv_uploader = False
                            st.success("Chatbot re-initialized with new data!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error processing CSV: {e}")
                    else:
                        st.error("Please upload a CSV file.")


def display_chat_interface():
    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                if "verbose_output" in message and message["verbose_output"]:
                    with st.expander("🔍 View Code", expanded=False):
                        st.markdown(message["verbose_output"])
                if "plot" in message and message["plot"]:
                    st.image(message["plot"])
                if "content" in message and message["content"]: # Ensure content exists
                    st.markdown(message["content"])
            else: # User message
                st.markdown(message["content"]) 