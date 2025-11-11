import plotly.express as px
import streamlit as st
from pathlib import Path

# Use relative path that works both locally and on server
file_path = Path(__file__).parent.parent / "media" / "disconnection_map.html"

if file_path.exists():
    with file_path.open('r') as file:
        html_map_1 = file.read()
    
    # make map bigger height and width
    st.components.v1.html(html_map_1, width="100%", height=1000)
else:
    st.error(f"Map file not found at: {file_path}")