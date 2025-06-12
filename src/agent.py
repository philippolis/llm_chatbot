from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
import streamlit as st
import pandas as pd
import os

def load_prompt(include_visualisations: bool = True, simple_language: bool = False):
    """Load the appropriate prompt from text files based on configuration."""
    
    # Determine the filename based on parameters
    if simple_language and include_visualisations:
        filename = "easy_language_incl_viz.txt"
    elif simple_language and not include_visualisations:
        filename = "easy_language_no_viz.txt"
    elif not simple_language and include_visualisations:
        filename = "hard_language_incl_viz.txt"
    else:  # not simple_language and not include_visualisations
        filename = "hard_language_no_viz.txt"
    
    # Load the prompt from file
    prompt_path = os.path.join("prompts", filename)
    
    try:
        with open(prompt_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        # Fallback to basic prompt if file not found
        return "You are a helpful data analysis assistant. You have access to these tools:"

def create_agent(df: pd.DataFrame, include_visualisations: bool = True, simple_language: bool = False):
    """Create a Pandas DataFrame agent with improved context understanding."""
    
    # Load the appropriate prompt from external file
    prefix = load_prompt(include_visualisations, simple_language)
    
    return create_pandas_dataframe_agent(
        ChatOpenAI(temperature=0, model=st.session_state["openai_model"]),
        df,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        allow_dangerous_code=True,
        prefix=prefix
    )

def get_agent():
    """
    Retrieves or creates the agent. If accessibility settings have changed,
    it recreates the agent.
    """
    df = st.session_state.get("df")
    if df is None:
        return None

    agent = st.session_state.get("agent")
    
    # Get current settings from session state
    include_visualisations = st.session_state.get("include_visualisations", True)
    simple_language = st.session_state.get("simple_language", False)

    # Get settings stored with the agent, if they exist
    agent_settings = st.session_state.get("agent_settings", {})
    
    # Check if settings have changed or if agent does not exist
    if (agent is None or
        agent_settings.get("include_visualisations") != include_visualisations or
        agent_settings.get("simple_language") != simple_language):
        
        # Store the new settings
        new_settings = {
            "include_visualisations": include_visualisations,
            "simple_language": simple_language
        }
        st.session_state.agent_settings = new_settings
        
        # Create a new agent
        agent = create_agent(
            df,
            include_visualisations=include_visualisations,
            simple_language=simple_language
        )
        st.session_state.agent = agent
        
    return agent 