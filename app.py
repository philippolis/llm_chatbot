import sys
import io
import streamlit as st
import pandas as pd

from src.state import init_session_state
from src.ui import display_setup_expander, display_chat_interface
from src.utils import format_verbose_output, capture_and_display_plot
from src.agent import create_agent

# Initialize session state
init_session_state()

# --- Default Agent Initialization ---
if st.session_state.agent is None:
    try:
        with st.spinner("Loading Titanic Dataset and Initializing Agent..."):
            titanic_url = "https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv"
            default_df = pd.read_csv(titanic_url)
            st.session_state.df = default_df
            
            st.session_state.agent = create_agent(
                default_df,
                # Use default accessibility options
                include_visualisations=st.session_state.include_visualisations,
                simple_language=st.session_state.simple_language
            )
            st.session_state.data_source_locked = True
    except Exception as e:
        st.error(f"Failed to initialize default agent with Titanic dataset: {e}")

st.title("Chatbot für Datenanalyse")

# --- Main App Logic ---
display_setup_expander()

display_chat_interface()

# Chat input and interaction logic
if st.session_state.agent:
    if prompt := st.chat_input("Ask questions about your data..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        assistant_response_content = "Sorry, I encountered an error and couldn't respond."
        plot_bytes_for_this_message = None
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
                    recent_messages = st.session_state.messages[-6:]  # Last 3 user-assistant pairs
                    for msg in recent_messages:
                        if msg["role"] == "user":
                            conversation_context += f"User: {msg['content']}\n"
                        elif msg["role"] == "assistant":
                            conversation_context += f"Assistant: {msg['content']}\n"
                    conversation_context += "\nCurrent question:\n"
                
                # Add context to the current prompt
                enhanced_prompt = f"{conversation_context}{prompt}"
                
                api_response = st.session_state.agent.invoke(enhanced_prompt)
                sys.stdout = old_stdout # Restore stdout
                verbose_agent_output = captured_output_buffer.getvalue()
                
                response_content = api_response.get('output', "No textual output from agent.")
                assistant_response_content = response_content
                
                if verbose_agent_output:
                    formatted_verbose_output = format_verbose_output(verbose_agent_output, response_content)
                    if formatted_verbose_output:
                        with st.expander("🔍 View Code", expanded=False):
                            st.markdown(formatted_verbose_output)
                        verbose_output_for_this_message = formatted_verbose_output

                if st.session_state.include_visualisations:
                    plot_bytes_for_this_message = capture_and_display_plot()
                
                if response_content: # Ensure content exists before marking it as "Answer"
                    st.markdown(response_content)

            except Exception as e:
                sys.stdout = old_stdout # Restore stdout in case of error during agent execution
                st.error(f"Error during agent execution: {e}")

        # Add assistant's full response to chat history
        current_assistant_message = {"role": "assistant", "content": assistant_response_content}
        if verbose_output_for_this_message:
            current_assistant_message["verbose_output"] = verbose_output_for_this_message
        if plot_bytes_for_this_message:
            current_assistant_message["plot"] = plot_bytes_for_this_message
        st.session_state.messages.append(current_assistant_message)
else:
    st.info("Please configure the settings and load data to start the chatbot.")