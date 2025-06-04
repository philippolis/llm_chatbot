import sys
import io
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from threading import RLock
import re
import ast # For safely parsing arguments string

_lock = RLock()

# Helper function to format the agent's verbose output for OpenAI Functions agent
def format_verbose_output(verbose_str: str, final_agent_answer_str: str) -> str:
    # Remove ANSI escape codes
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    clean_str = ansi_escape.sub('', verbose_str)
    # Also clean the final answer string for accurate comparison/replacement
    final_answer_cleaned = ansi_escape.sub('', final_agent_answer_str).strip()

    formatted_parts = []

    # Find the primary invocation of python_repl_ast
    invocation_match = re.search(r"Invoking: `python_repl_ast` with `(\{.*?\})`", clean_str, re.DOTALL)
    
    if invocation_match:
        args_str = invocation_match.group(1)
        code_to_execute = args_str # Default to raw args_str if specific parsing fails
        try:
            # ast.literal_eval can parse string representation of dicts, lists, etc.
            args_dict = ast.literal_eval(args_str)
            if isinstance(args_dict, dict) and 'query' in args_dict:
                code_to_execute = args_dict['query']
        except (SyntaxError, ValueError, TypeError) as e_eval:
            query_extract_match = re.search(r"['\"]query['\"]\s*:\s*['\"](.*?)['\"]\s*(?:,\s*.*?)?\}", args_str, re.DOTALL)
            if query_extract_match:
                code_to_execute = query_extract_match.group(1).encode('utf-8').decode('unicode_escape', 'ignore')

        formatted_parts.append(f"**Code Executed:**\n```python\n{code_to_execute.strip()}\n```")
        
        end_of_invocation_idx = invocation_match.end()
        text_after_invocation = clean_str[end_of_invocation_idx:]
        finished_chain_match = re.search(r">\s*Finished chain\.", text_after_invocation, re.DOTALL)
        
        if finished_chain_match:
            intermediate_text = text_after_invocation[:finished_chain_match.start()].strip()
        else:
            intermediate_text = text_after_invocation.strip()
        
        observation = intermediate_text.replace(final_answer_cleaned, "").strip()
        
        if observation:
            formatted_parts.append(f"**Result:**\n```text\n{observation}\n```")
    
    if not formatted_parts and clean_str.strip() and clean_str.strip() != final_answer_cleaned:
        formatted_parts.append(f"**Agent Log:**\n```text\n{clean_str.strip()}\n```")
    
    if not formatted_parts:
        return "" 

    return "\n\n".join(formatted_parts)

# Initialize session state variables
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


# --- Main App Logic ---

if not st.session_state.data_source_locked:
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
                    st.session_state.agent = create_pandas_dataframe_agent(
                        ChatOpenAI(temperature=0, model=st.session_state["openai_model"]),
                        st.session_state.df,
                        verbose=True,
                        agent_type=AgentType.OPENAI_FUNCTIONS,
                        allow_dangerous_code=True
                    )
                    st.session_state.data_source_locked = True
                    st.session_state.messages = [] # Clear previous messages for the new session
                    st.success("Chatbot initialized successfully!")
                    st.rerun() # Rerun to switch to the chat interface
                except Exception as e:
                    st.error(f"Error creating chatbot agent: {e}")
                    st.session_state.agent = None
                    # Keep df loaded if agent creation fails, user might want to retry or debug
            else:
                # Error message for df loading should have already been displayed
                pass
else:
    # --- Chat Interface (Data Source is Locked) ---
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

    # Chat input and interaction logic
    if st.session_state.agent is None:
        st.error("Agent not initialized. Please try reloading or check setup.")
    else:
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
                    api_response = st.session_state.agent.invoke(prompt)
                    sys.stdout = old_stdout # Restore stdout
                    verbose_agent_output = captured_output_buffer.getvalue()
                    
                    response_content = api_response.get('output', "No textual output from agent.")
                    assistant_response_content = response_content
                    
                    if verbose_agent_output:
                        formatted_verbose_output = format_verbose_output(verbose_agent_output, response_content)
                        if formatted_verbose_output:
                            st.markdown(formatted_verbose_output)
                            verbose_output_for_this_message = formatted_verbose_output

                    with _lock: # Matplotlib plot capturing
                        fig = plt.gcf()
                        if fig and fig.get_axes():
                            img_buffer = io.BytesIO()
                            fig.savefig(img_buffer, format="png")
                            img_buffer.seek(0)
                            plot_bytes_for_this_message = img_buffer.getvalue()
                            st.image(plot_bytes_for_this_message)
                            plt.clf()
                            plt.close(fig)
                    
                    if response_content: # Ensure content exists before marking it as "Answer"
                        st.markdown("**Answer:**")
                        st.markdown(response_content)

                except Exception as e:
                    sys.stdout = old_stdout # Restore stdout in case of error during agent execution
                    st.error(f"Error during agent execution: {e}")
                    # assistant_response_content is already set to an error message

            # Add assistant's full response to chat history
            current_assistant_message = {"role": "assistant", "content": assistant_response_content}
            if verbose_output_for_this_message:
                current_assistant_message["verbose_output"] = verbose_output_for_this_message
            if plot_bytes_for_this_message:
                current_assistant_message["plot"] = plot_bytes_for_this_message
            st.session_state.messages.append(current_assistant_message)