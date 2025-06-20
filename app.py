import sys
import io
import streamlit as st
import pandas as pd

from src.state import init_session_state
from src.ui import display_setup_section, display_chat_interface
from src.utils import format_verbose_output, capture_and_display_plots
from src.agent import get_agent

# Initialize session state
init_session_state()

# --- Default Dataset Loading ---
if st.session_state.df is None:
    try:
        with st.spinner("Lade Titanic-Datensatz..."):
            titanic_url = "https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv"
            default_df = pd.read_csv(titanic_url)
            st.session_state.df = default_df
            st.session_state.data_source_name = "Titanic"
    except Exception as e:
        st.error(f"Fehler beim Laden des Titanic-Datensatzes: {e}")

st.markdown('<h1 tabindex="0">Chatbot für Datenanalyse</h1>', unsafe_allow_html=True)
st.markdown('<h2 tabindex="0">Datensatz</h2>', unsafe_allow_html=True)
st.markdown(f'<div tabindex="0">Aktuell verwendeter Datensatz: <strong>{st.session_state.data_source_name}</strong></div>', unsafe_allow_html=True)

# Load and display dataset description
try:
    # Assuming data_description.txt is in the same directory as app.py
    with open("data_description.txt", "r", encoding="utf-8") as f:
        dataset_description = f.read()
    st.markdown(f'<div tabindex="0" style="text-align: justify;">{dataset_description}</div>', unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("Keine Beschreibung für den Datensatz gefunden (data_description.txt nicht gefunden).")

if st.session_state.df is not None:
    st.markdown('<h3 tabindex="0">Vorschau des Datensatzes</h3>', unsafe_allow_html=True)
    
    num_rows, num_cols = st.session_state.df.shape
    st.markdown(f'<div tabindex="0">Anzahl der Zeilen: <strong>{num_rows}</strong></div>', unsafe_allow_html=True)
    st.markdown(f'<div tabindex="0">Anzahl der Spalten: <strong>{num_cols}</strong></div>', unsafe_allow_html=True)

    st.dataframe(st.session_state.df.head())

# --- Main App Logic ---
display_setup_section()

display_chat_interface()

# Get the agent, which will be created or recreated if necessary
agent = get_agent()

# Chat input and interaction logic
if agent:
    if prompt := st.chat_input("Stellen Sie Fragen zu Ihren Daten..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(f'<div tabindex="0">{prompt}</div>', unsafe_allow_html=True)

        assistant_response_content = "Entschuldigung, ein Fehler ist aufgetreten und ich konnte nicht antworten."
        plots_bytes_for_this_message = []
        verbose_output_for_this_message = None

        with st.chat_message("assistant"):
            old_stdout = sys.stdout
            sys.stdout = captured_output_buffer = io.StringIO()
            
            try:
                # Build conversation context from previous messages for better context awareness
                conversation_context = ""
                if st.session_state.messages:
                    conversation_context = "\n\nPrevious conversation context:\n"
                    # Only include the last 3-4 exchanges to avoid token limit issues
                    recent_messages = st.session_state.messages[-6:]  # Last 3 user-assistant pair
                    for msg in recent_messages:
                        if msg["role"] == "user":
                            conversation_context += f"User: {msg['content']}\n"
                        elif msg["role"] == "assistant":
                            conversation_context += f"Assistant: {msg['content']}\n"
                    conversation_context += "\nCurrent question:\n"
                
                # Add context to the current prompt
                enhanced_prompt = f"{conversation_context}{prompt}"
                
                api_response = agent.invoke(enhanced_prompt)
                sys.stdout = old_stdout # Restore stdout
                verbose_agent_output = captured_output_buffer.getvalue()
                
                response_content = api_response.get('output', "Keine textliche Ausgabe vom Agenten.")
                assistant_response_content = response_content
                
                if verbose_agent_output:
                    formatted_verbose_output = format_verbose_output(verbose_agent_output, response_content)
                    if formatted_verbose_output:
                        if st.session_state.get("show_code", True):
                            with st.expander("🔍 Code anzeigen", expanded=False):
                                st.markdown(formatted_verbose_output)
                        verbose_output_for_this_message = formatted_verbose_output

                if st.session_state.include_visualisations:
                    plots_bytes_for_this_message = capture_and_display_plots()
                
                if response_content: # Ensure content exists before marking it as "Answer"
                    st.markdown(f'<div tabindex="0">{response_content}</div>', unsafe_allow_html=True)

            except Exception as e:
                sys.stdout = old_stdout # Restore stdout in case of error during agent execution
                st.error(f"Fehler bei der Ausführung des Agenten: {e}")

        # Add assistant's full response to chat history
        current_assistant_message = {"role": "assistant", "content": assistant_response_content}
        if verbose_output_for_this_message:
            current_assistant_message["verbose_output"] = verbose_output_for_this_message
        if plots_bytes_for_this_message:
            current_assistant_message["plots"] = plots_bytes_for_this_message
        st.session_state.messages.append(current_assistant_message)
else:
    st.info("Bitte konfigurieren Sie die Einstellungen und laden Sie Daten, um den Chatbot zu starten.")