import re
import ast
import io
from threading import RLock
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

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

def capture_and_display_plot():
    """Captures the current matplotlib plot, displays it in Streamlit,
    and returns it as bytes for saving in session state."""
    with _lock:
        fig = plt.gcf()
        if fig and fig.get_axes():
            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format="png")
            img_buffer.seek(0)
            plot_bytes = img_buffer.getvalue()
            st.image(plot_bytes)
            plt.clf()
            plt.close(fig)
            return plot_bytes
    return None 