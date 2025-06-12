import streamlit as st
from src.agent import create_agent

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