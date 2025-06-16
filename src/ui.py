import streamlit as st
import pandas as pd
from src.agent import get_agent

def display_setup_section():
    st.header("Barrierefreiheitsoptionen")
    st.toggle(
        "Visualisierungen in Antworten einbeziehen",
        key="include_visualisations",
        help="Wenn aktiviert, können Diagramme und Grafiken in den Antworten angezeigt werden."
    )
    st.toggle(
        "Einfache Sprache verwenden",
        key="simple_language",
        help="Wenn aktiviert, werden komplexe Begriffe vermieden und einfachere Formulierungen verwendet."
    )
    st.toggle(
        "Die Option 'Code anzeigen' anbieten",
        key="show_code",
        help="Wenn aktiviert, kann der zugrunde liegende Code für eine Antwort angezeigt werden."
    )

    st.header("Chat-Verlauf")

def display_chat_interface():
    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                if st.session_state.get("show_code", True) and "verbose_output" in message and message["verbose_output"]:
                    with st.expander("🔍 Code anzeigen", expanded=False):
                        st.markdown(message["verbose_output"])
                if "plot" in message and message["plot"]:
                    st.image(message["plot"])
                if "content" in message and message["content"]: # Ensure content exists
                    st.markdown(message["content"])
            else: # User message
                st.markdown(message["content"])