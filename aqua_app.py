import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium import plugins
import geopandas as gpd
from PIL import Image

import pickle
from pathlib import Path
import streamlit_authenticator as stauth

st.set_page_config(
    page_title="Chile Aquaculture Data",
    page_icon="🐟",
    layout="wide"
)

pages = {
        "Data Exploration": [
            st.Page('pages/page0_home.py', title="Home"),
            # st.Page('pages/page1_salmon_complaints.py', title="Salmon Concessions & Complaints"),
            st.Page('pages/page2_sensors.py', title="Sensors"),
            st.Page('pages/page3_production.py', title="Production"),
            st.Page('pages/page3b_production_movement.py', title="Ownership and Production Trends"),
            st.Page('pages/page4_environmental.py', title="Environmental Impacts")
            
        ],
        "External Datasets": [
            st.Page('pages/page5_other.py', title="Other Visualizations")
        ],
    }

pg = st.navigation(pages)

### User Authentication
names = ["aquaculture chile app"]
usernames = ["aquaculture-chile-app"]

file_path = Path(__file__).parent / "config/hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)
    
authenticator = stauth.Authenticate(
    names=names,
    usernames=usernames,
    passwords=hashed_passwords,
    cookie_name="aqua_cookie",
    key="abcdef",
    cookie_expiry_days=5,
)

name, authentication_status, username = authenticator.login("Aquaculture Chile Login", "main")

def finish_session():
    authenticator.logout("End Session", "sidebar")

import os 
if authentication_status == False:
    st.error("Username/password is incorrect")
elif authentication_status == None:
    st.warning("Please enter your username and password")
elif authentication_status == True:
    pg.run()
    st.sidebar.write(f"Welcome to the Aquaculture Chile App!")
    st.sidebar.button("End Session", on_click=finish_session)


## personal

