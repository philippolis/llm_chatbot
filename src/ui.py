import streamlit as st
import pandas as pd
from src.agent_manager import get_agent

def display_setup_expander():
    # The expander will now be open by default.
    with st.expander("⚙️ Einstellungen und Datenquelle", expanded=True):
        st.header("Barrierefreiheitsoptionen")
        st.toggle(
            "Visualisierungen in Antworten einbeziehen?", 
            key="include_visualisations"
        )
        st.toggle(
            "Einfache Sprache verwenden?", 
            key="simple_language"
        )

        st.header("Datenquelle")
        
        if not st.session_state.show_csv_uploader:
            st.info(f"Aktuell verwendet: **{st.session_state.data_source_name}**.")
            if st.button("Datensatz ändern"):
                st.session_state.show_csv_uploader = True
                st.rerun()
        else:
            with st.form("data_source_form"):
                uploaded_file_value = st.file_uploader(
                    "Laden Sie Ihre CSV-Datei hoch", 
                    type="csv", 
                    key="csv_uploader"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("CSV laden und neu initialisieren")
                with col2:
                    if st.form_submit_button("Abbrechen"):
                        st.session_state.show_csv_uploader = False
                        st.rerun()

                if submitted:
                    if uploaded_file_value is not None:
                        try:
                            current_df = pd.read_csv(uploaded_file_value)
                            st.session_state.df = current_df
                            st.session_state.data_source_name = uploaded_file_value.name
                            
                            # Force agent recreation on next get_agent() call
                            st.session_state.agent = None
                            st.session_state.agent_settings = {}
                            
                            st.session_state.data_source_locked = True
                            st.session_state.messages = []
                            st.session_state.show_csv_uploader = False
                            st.success("Chatbot mit neuen Daten neu initialisiert!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Fehler beim Verarbeiten der CSV-Datei: {e}")
                    else:
                        st.error("Bitte laden Sie eine CSV-Datei hoch.")


def display_chat_interface():
    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                if "verbose_output" in message and message["verbose_output"]:
                    with st.expander("🔍 Code anzeigen", expanded=False):
                        st.markdown(message["verbose_output"])
                if "plot" in message and message["plot"]:
                    st.image(message["plot"])
                if "content" in message and message["content"]: # Ensure content exists
                    st.markdown(message["content"])
            else: # User message
                st.markdown(message["content"]) 