from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
import streamlit as st
import pandas as pd

def create_agent(df: pd.DataFrame):
    """Create a Pandas DataFrame agent."""
    return create_pandas_dataframe_agent(
        ChatOpenAI(temperature=0, model=st.session_state["openai_model"]),
        df,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        allow_dangerous_code=True
    ) 