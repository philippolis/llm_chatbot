from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from openai import OpenAI
import streamlit as st
import pandas as pd
from langchain_openai import OpenAI
import matplotlib.pyplot as plt

df = pd.read_csv(
    "https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv"
)

st.title("ChatGPT-like clone")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4.1-nano"

agent = create_pandas_dataframe_agent(
    ChatOpenAI(temperature=0, model=st.session_state["openai_model"]),
    df,
    verbose=True,
    agent_type=AgentType.OPENAI_FUNCTIONS,
    allow_dangerous_code=True
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_response_id" not in st.session_state:
    st.session_state.last_response_id = None

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How many rows are there?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Call the Responses API
        api_response = agent.invoke(prompt)

        # Extract the response text from the API response object
        # Based on OpenAI cookbook examples for the Responses API
        response_content = api_response['output']
        
        # Attempt to display matplotlib plot if one was generated
        fig = plt.gcf() # Get current figure
        # Check if the figure actually contains something (e.g., has axes)
        if fig and fig.get_axes():
            st.pyplot(fig)
            plt.clf()  # Clear the current figure to prevent it from being re-used
            plt.close(fig) # Close the figure object to release memory
        
        st.markdown(response_content)

    st.session_state.messages.append({"role": "assistant", "content": response_content})