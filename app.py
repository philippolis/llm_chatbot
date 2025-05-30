from openai import OpenAI
import streamlit as st

st.title("ChatGPT-like clone")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4.1-nano"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_response_id" not in st.session_state:
    st.session_state.last_response_id = None

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        api_params = {
            "model": st.session_state["openai_model"],
            "input": prompt,
        }
        if st.session_state.last_response_id:
            api_params["previous_response_id"] = st.session_state.last_response_id

        # Call the Responses API
        api_response = client.responses.create(**api_params)

        # Extract the response text from the API response object
        # Based on OpenAI cookbook examples for the Responses API
        response_content = api_response.output_text

        # Update the last_response_id for the next turn
        st.session_state.last_response_id = api_response.id
        
        st.markdown(response_content)

    st.session_state.messages.append({"role": "assistant", "content": response_content})