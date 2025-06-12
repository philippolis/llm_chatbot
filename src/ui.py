import streamlit as st
import pandas as pd
from src.agent import create_agent

def display_data_source_form():
    st.title("Chatbot Setup: Choose Your Data")

    with st.form("data_source_form"):
        data_source_choice = st.radio(
            "How would you like to provide data?",
            ("Use **Titanic dataset** as an example", "Upload a **CSV file**"),
            key="data_source_radio"
        )
        
        uploaded_file_value = None
        if data_source_choice == "Upload a **CSV file**":
            uploaded_file_value = st.file_uploader("Upload your CSV file", type="csv", key="csv_uploader")

        submitted = st.form_submit_button("Load Data and Initialize Chatbot")

        if submitted:
            current_df = None
            if data_source_choice == "Use **Titanic dataset** as an example":
                try:
                    titanic_url = "https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv"
                    current_df = pd.read_csv(titanic_url)
                    st.session_state.df = current_df
                    st.success("Titanic dataset loaded successfully!")
                except Exception as e:
                    st.error(f"Error loading Titanic dataset: {e}")
                    st.session_state.df = None
            
            elif data_source_choice == "Upload a **CSV file**":
                if uploaded_file_value is not None:
                    try:
                        current_df = pd.read_csv(uploaded_file_value)
                        st.session_state.df = current_df
                        st.success("CSV file loaded and parsed successfully!")
                    except Exception as e:
                        st.error(f"Error reading or parsing uploaded CSV file: {e}")
                        st.session_state.df = None
                else:
                    st.error("Please upload a CSV file if you choose that option.")
                    st.session_state.df = None
            
            if st.session_state.df is not None:
                try:
                    st.session_state.agent = create_agent(st.session_state.df)
                    st.session_state.data_source_locked = True
                    st.session_state.messages = [] # Clear previous messages for the new session
                    st.success("Chatbot initialized successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating chatbot agent: {e}")
                    st.session_state.agent = None
            else:
                pass


def display_chat_interface():
    st.title("Chatbot für Datenanalyse")

    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                if "verbose_output" in message and message["verbose_output"]:
                    st.markdown(message["verbose_output"])
                if "plot" in message and message["plot"]:
                    st.image(message["plot"])
                if "content" in message and message["content"]: # Ensure content exists
                    st.markdown("**Answer:**")
                    st.markdown(message["content"])
            else: # User message
                st.markdown(message["content"]) 