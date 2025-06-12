import io
from threading import RLock
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

_lock = RLock()

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