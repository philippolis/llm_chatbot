from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
import streamlit as st
import pandas as pd

def create_agent(df: pd.DataFrame):
    """Create a Pandas DataFrame agent with improved context understanding."""
    
    # Custom prefix to help the agent understand context and references
    prefix = """
You are a helpful data analysis assistant working with a pandas dataframe named `df`. 
When users refer to "this", "it", "that", or similar pronouns, they are typically referring to:
- The data or results from their previous question
- A specific column, chart, or analysis they mentioned earlier
- The same data subset or filtered data from the previous operation

Pay attention to the conversation context provided to understand what the user is referring to.
Use seaborn for creating plots and visualizations.

You have access to these tools:
"""
    
    return create_pandas_dataframe_agent(
        ChatOpenAI(temperature=0, model=st.session_state["openai_model"]),
        df,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        allow_dangerous_code=True,
        prefix=prefix
    ) 