import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
from pathlib import Path


# spinner until the entire page is loaded
with st.spinner("Loading page..."):
    # pause for 3 seconds
    time.sleep(3)

@st.cache_data()
def load_html_map():
    # Use relative path that works both locally and on server
    file_path = Path(__file__).parent.parent / "media" / "concession_eda_production_bubble_map2.html"
    
    if not file_path.exists():
        # Debug: show what files are in the media directory
        media_dir = Path(__file__).parent.parent / "media"
        error_msg = f"Map file not found at: {file_path}\n\n"
        if media_dir.exists():
            error_msg += f"Media directory exists at: {media_dir}\n"
            error_msg += f"Files in media directory: {list(media_dir.iterdir())}\n"
        else:
            error_msg += f"Media directory does not exist at: {media_dir}\n"
            error_msg += f"Project root: {Path(__file__).parent.parent}\n"
        raise FileNotFoundError(error_msg)
    
    with file_path.open('r') as file:
        html_map = file.read()
    return html_map

# title
st.title("Welcome to the Chile Aquaculture Project")
# display the html map
try:
    st.components.v1.html(load_html_map(), width="100%", height=900)
except FileNotFoundError as e:
    st.error(f"Could not load map file. Please ensure the media folder is deployed to the server.\n\n{str(e)}")