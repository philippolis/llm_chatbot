from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
import streamlit as st
import pandas as pd

def create_agent(df: pd.DataFrame, include_visualisations: bool = True, simple_language: bool = False):
    """Create a Pandas DataFrame agent with improved context understanding."""
    
    # Custom prefix to help the agent understand context and references
    prefix = """
You are a helpful data analysis assistant working with a pandas dataframe named `df`. 
When users refer to "this", "it", "that", or similar pronouns, they are typically referring to:
- The data or results from their previous question
- A specific column, chart, or analysis they mentioned earlier
- The same data subset or filtered data from the previous operation

Pay attention to the conversation context provided to understand what the user is referring to.

Please use your common sense to explain how the findings can be understood or when the user might misunderstand the data.

If the user's prompt doesn't resemble a question or command related to data analysis (e.g., "Testing this", "Hello", or other non-analytical input), respond with a helpful list of things they could do with the data, such as:
- Explore the dataset structure and basic information
- Calculate summary statistics
- Create visualizations and charts
- Filter and analyze specific subsets
- Compare different groups or categories
- Identify trends and patterns
- Generate insights and recommendations
"""

    if simple_language:
        prefix += "\nAfter your code execution, explain your findings in simple, easy-to-understand language. Avoid jargon."

    if include_visualisations:
        prefix += """
Choose the most appropriate response format based on the user's question:
- **Single number/statistic**: For questions asking for counts, averages, totals, percentages, or specific calculated values
- **Markdown table**: For questions requesting comparisons, summaries, grouped data, or when showing multiple related values
- **Seaborn plot**: For questions about trends, distributions, relationships, patterns, or when visual representation would be most informative

Use seaborn for creating plots and visualizations. Always consider which format would best answer the user's specific question.
"""
    else:
        prefix += """
Choose the most appropriate response format based on the user's question:
- **Single number/statistic**: For questions asking for counts, averages, totals, percentages, or specific calculated values
- **Markdown table**: For questions requesting comparisons, summaries, grouped data, or when showing multiple related values

Do not create plots or visualizations. Provide answers in text or markdown tables.
"""
    prefix += "\nAlways print out relevant results."
    prefix += "\nYou have access to these tools:"
    
    return create_pandas_dataframe_agent(
        ChatOpenAI(temperature=0, model=st.session_state["openai_model"]),
        df,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        allow_dangerous_code=True,
        prefix=prefix
    ) 