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

Choose the most appropriate response format based on the user's question:
- **Single number/statistic**: For questions asking for counts, averages, totals, percentages, or specific calculated values
- **Markdown table**: For questions requesting comparisons, summaries, grouped data, or when showing multiple related values
- **Seaborn plot**: For questions about trends, distributions, relationships, patterns, or when visual representation would be most informative

Use seaborn for creating plots and visualizations. Always consider which format would best answer the user's specific question.

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