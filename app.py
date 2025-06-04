import sys
import io
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from openai import OpenAI
import streamlit as st
import pandas as pd
from langchain_openai import OpenAI
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
            # Fallback for complex cases or if ast.literal_eval fails (e.g. unescaped internal quotes)
            # Try a more direct regex for the common {'query': "\"..."\"} structure
            query_extract_match = re.search(r"['\"]query['\"]\s*:\s*['\"](.*?)['\"]\s*(?:,\s*.*?)?\}\"", args_str, re.DOTALL)
            if query_extract_match:
                # .decode('unicode_escape') handles things like \n within the code string literal itself
                code_to_execute = query_extract_match.group(1).encode('utf-8').decode('unicode_escape', 'ignore')

        formatted_parts.append(f"**Code Executed:**\n```python\n{code_to_execute.strip()}\n```")

        # Determine the text block that contains the observation and potentially the final answer.
        # This block is after the invocation and before the "> Finished chain." marker.
        end_of_invocation_idx = invocation_match.end()
        text_after_invocation = clean_str[end_of_invocation_idx:]
        
        finished_chain_match = re.search(r">\s*Finished chain\.", text_after_invocation, re.DOTALL)
        
        if finished_chain_match:
            intermediate_text = text_after_invocation[:finished_chain_match.start()].strip()
        else:
            intermediate_text = text_after_invocation.strip()
        
        # The intermediate_text now likely contains the raw observation followed by the agent's final answer text.
        # We remove the known final_answer_cleaned to isolate the observation.
        observation = intermediate_text.replace(final_answer_cleaned, "").strip()
        
        if observation: # Only add if observation is non-empty after stripping and removing final answer
            formatted_parts.append(f"**Result:**\n```text\n{observation}\n```")
    
    # Fallback: If specific parsing failed but there's content not part of the final answer
    if not formatted_parts and clean_str.strip() and clean_str.strip() != final_answer_cleaned:
        formatted_parts.append(f"**Agent Log:**\n```text\n{clean_str.strip()}\n```")
    
    if not formatted_parts:
        return "" # Return empty if nothing distinct to show

    return "\n\n".join(formatted_parts) # Use more spacing for readability

st.title("Chatbot für Datenanalyse")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4.1-nano"

# Initialize df and agent in session_state if they don't exist
if 'df' not in st.session_state:
    st.session_state.df = None
if 'agent' not in st.session_state:
    st.session_state.agent = None

# Data source selection
data_source = st.radio(
    "Choose a data source:",
    ("Use Titanic dataset (default)", "Upload a CSV file"),
    key="data_source_selector"
)

uploaded_file = None
if data_source == "Upload a CSV file":
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        try:
            st.session_state.df = pd.read_csv(uploaded_file)
            st.success("CSV file loaded successfully!")
        except Exception as e:
            st.error(f"Error loading CSV: {e}")
            st.session_state.df = None # Ensure df is None if loading fails
    elif st.session_state.df is not None and not data_source == "Use Titanic dataset (default)": # If no file is uploaded but one was previously
        pass # Keep existing df from previous upload unless user switches back to default
    else: # No file uploaded yet for this option
        st.session_state.df = None

elif data_source == "Use Titanic dataset (default)":
    # Only load if df is not already the titanic set or if it's None
    # This prevents reloading if user clicks away and back
    titanic_url = "https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv"
    # A simple way to check if current df is titanic is by checking one of its known properties
    # More robustly, we could store a flag or the source URL in session_state
    # For simplicity, we'll reload if df is None or if a file was previously uploaded.
    # A more robust check would be to see if st.session_state.df was loaded from the titanic_url
    # For this example, we'll reload if the source is switched to titanic.
    st.session_state.df = pd.read_csv(titanic_url)


# Create agent only if df is loaded
if st.session_state.df is not None:
    if st.session_state.agent is None or (uploaded_file is not None or data_source == "Use Titanic dataset (default)"): # Recreate agent if df changes
        try:
            st.session_state.agent = create_pandas_dataframe_agent(
                ChatOpenAI(temperature=0, model=st.session_state["openai_model"]),
                st.session_state.df,
                verbose=True,
                agent_type=AgentType.OPENAI_FUNCTIONS,
                allow_dangerous_code=True
            )
        except Exception as e:
            st.error(f"Error creating agent: {e}")
            st.session_state.agent = None # Ensure agent is None if creation fails
else:
    st.warning("Please upload a CSV file or select the default dataset to begin.")
    st.session_state.agent = None


if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_response_id" not in st.session_state:
    st.session_state.last_response_id = None

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            if "verbose_output" in message and message["verbose_output"]:
                st.markdown(message["verbose_output"])
            if "plot" in message and message["plot"]:
                st.image(message["plot"])
            if "content" in message and message["content"]:
                st.markdown("**Answer:**")
                st.markdown(message["content"])
        else: # User message
            st.markdown(message["content"])

if st.session_state.agent is not None: # Only show chat input if agent is ready
    if prompt := st.chat_input("How many rows are there?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        assistant_response_content = ""
        plot_bytes_for_this_message = None
        verbose_output_for_this_message = None # ADDED: To store verbose output for current message

        with st.chat_message("assistant"):
            # Capture stdout for agent's verbose output
            old_stdout = sys.stdout
            sys.stdout = captured_output_buffer = io.StringIO()

            # Agent invocation (verbose output goes to captured_output_buffer)
            try:
                api_response = st.session_state.agent.invoke(prompt)
                 # Restore stdout
                sys.stdout = old_stdout
                verbose_agent_output = captured_output_buffer.getvalue()

                # Extract the final response text from the API response object
                response_content = api_response['output']
                assistant_response_content = response_content # Store for adding to history later
                
                # Display Agent's verbose output (if any)
                if verbose_agent_output:
                    formatted_verbose_output = format_verbose_output(verbose_agent_output, response_content)
                    if formatted_verbose_output: # Check if there's actually anything to display
                        st.markdown(formatted_verbose_output)
                        verbose_output_for_this_message = formatted_verbose_output # Store for history

                # Attempt to capture and display matplotlib plot if one was generated
                with _lock:
                    fig = plt.gcf() # Get current figure
                    # Check if the figure actually contains something (e.g., has axes)
                    if fig and fig.get_axes():
                        img_buffer = io.BytesIO()
                        fig.savefig(img_buffer, format="png")
                        img_buffer.seek(0)
                        plot_bytes_for_this_message = img_buffer.getvalue() # Store bytes
                        
                        st.image(plot_bytes_for_this_message) # Display current plot immediately
                        
                        plt.clf()  # Clear the current figure to prevent it from being re-used
                        plt.close(fig) # Close the figure object to release memory
                
                # Display the final answer from the agent
                if response_content: # Check if there's actual text content to display
                    st.markdown("**Answer:**")
                    st.markdown(response_content)
            except Exception as e:
                sys.stdout = old_stdout # Restore stdout in case of error
                st.error(f"Error during agent execution: {e}")
                assistant_response_content = "Sorry, I encountered an error."


        # Add assistant's response (and plot, if any) to chat history
        assistant_message_data = {"role": "assistant", "content": assistant_response_content}
        if verbose_output_for_this_message:
            assistant_message_data["verbose_output"] = verbose_output_for_this_message
        if plot_bytes_for_this_message:
            assistant_message_data["plot"] = plot_bytes_for_this_message
        st.session_state.messages.append(assistant_message_data)
else:
    # This part is to ensure chat history is still displayed even if agent is not ready
    # We don't show the chat input, but historical messages are good to keep.
    pass