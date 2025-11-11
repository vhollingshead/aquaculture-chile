import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
from utils.utils_webapp import process_dataframe_coordinates, db_connect, load_secrets
import yaml
import os
import sys
from pyprojroot import here
import psycopg2
import sshtunnel

# from st_files_connection import FilesConnection

# Create connection object and retrieve file contents.
# Specify input format is a csv and to cache the result for 600 seconds.
# conn = st.connection('gcs', type=FilesConnection)
# aqua_tipline = conn.read("https://storage.googleapis.com/aquaculture-chile/external_datasets/aquaculture_tips.xlsx", input_format="csv", ttl=600)
# st.dataframe(aqua_tipline)


# secrets = load_secrets() # takes in secrets_path, but default is the expected location of config/secrets.yaml
# eng, tunnel = db_connect(secrets)
# with eng.connect() as conn:
#     df = pd.read_sql("select * from raw.sensor_devices", conn)
#     # geo_df = gpd.read_postgis("select * from geo.tiles limit 1000", conn, geom_col = 'geometry')

# # At the end, when you're done with the sql connection. Otherwise, trying to open multiple engines/tunnels on the same port will throw issues
# eng.dispose()

# # Set up imports from the utils directory
# root = here() 
# sys.path.insert(1, str(here()))

# secrets = load_secrets() # takes in secrets_path, but default is the expected location of config/secrets.yaml
# eng, tunnel = db_connect(secrets)
# with eng.connect() as conn:
#     concessions_2024 = pd.read_sql("select * from raw.concessions_2024", conn)
#     IdSea_Rna = pd.read_sql("select * from raw.ids_xwalk", conn)
#     production_limits_df = pd.read_sql("select * from raw.production_limits", conn)
#     aqua_tipline = pd.read_sql("select * from raw.aquaculture_tips", conn)

# conn = st.connection("postgresql", type="sql")

# # concessions_2024 = conn.query("select * from raw.concessions_2024")
# IdSea_Rna = conn.query("select * from raw.ids_xwalk")
# production_limits_df = conn.query("select * from raw.production_limits")
# aqua_tipline = conn.query("select * from raw.aquaculture_tips")

# # st.dataframe(concessions_2024)
# st.dataframe(IdSea_Rna)
# st.dataframe(production_limits_df)
# st.dataframe(aqua_tipline)

# Connect to database using SSH tunnel
secrets = load_secrets()
eng, tunnel = db_connect(secrets)

with eng.connect() as conn:
    concessions_2024 = pd.read_sql("select * from raw.concessions_2024", conn)
    aqua_tipline = pd.read_sql("select * from raw.aquaculture_tips", conn)
    production_limits_df = pd.read_sql("select * from raw.production_limits", conn)
    IdSea_Rna = pd.read_sql("select * from raw.ids_xwalk", conn)

# Clean up connection
eng.dispose()
if tunnel:
    tunnel.stop()

st.dataframe(concessions_2024)
st.dataframe(aqua_tipline)
st.dataframe(production_limits_df)
st.dataframe(IdSea_Rna)

# # DATA CLEANING - to be updated in postgres database

# # convert all Production Limits to tons
# production_limits_df['Production_Limit_ton_calculated'] = production_limits_df.apply(lambda row: row['LimiteProduccion'] / 1000 if row['UnidadMedidaProduccionId'] == 2 else row['LimiteProduccion'], axis=1)
# # replace Producción with Nan in IdSea
# production_limits_df['IdSea'] = production_limits_df['IdSea'].replace('Producción)', np.nan) # only 10 cases of this
# production_limits_df['IdSea'] = production_limits_df['IdSea'].replace('Biomasa Último Año de', np.nan) # only 9 cases of this
# # remove nan in IdSea
# production_limits_df = production_limits_df[production_limits_df['IdSea'].notna()]
# # convert IdSea to int
# production_limits_df['IdSea'] = production_limits_df['IdSea'].astype(int)

# # rename N_CODIGOCE to Rna in concessions_2024
# concessions_2024 = concessions_2024.rename(columns={'N_CODIGOCE': 'Rna'})
# concessions_2024_lat_long = process_dataframe_coordinates(concessions_2024, 'COORDENADA')

# ### Salmon Concessions - IdSea + Technical Projects
# # drop nan in ESPECIES
# concessions_2024_lat_long = concessions_2024_lat_long[concessions_2024_lat_long['ESPECIES'].notna()]
# # filter for cases where salmon is in ESPECIES
# concessions_2024_salmon = concessions_2024_lat_long[concessions_2024_lat_long['ESPECIES'].str.contains('SALMON')] # no Rna or IdSea yet
# # Salmon Concessions by Owner with Concessions Permit - Rna 
# concessions_2024_IdSea = pd.merge(concessions_2024_salmon, IdSea_Rna, on='Rna', how='left')

# # remove duplicate Rna from concessions_2024_salmon
# concessions_2024_salmon = concessions_2024_salmon.drop_duplicates(subset=['Rna'])
# print('length of concessions_2024_salmon:', len(concessions_2024_salmon))

# ### Concessions by Production
# # remove nan in IdSea
# concessions_2024_IdSea_not_null = concessions_2024_IdSea[concessions_2024_IdSea['IdSea'].notna()]
# # make IdSea an int
# concessions_2024_IdSea_not_null['IdSea'] = concessions_2024_IdSea_not_null['IdSea'].astype(int)
# production_limits_concessions_IdSea = pd.merge(concessions_2024_IdSea_not_null, production_limits_df, on='IdSea', how='left')
# concessions_2024_by_production = production_limits_concessions_IdSea[production_limits_concessions_IdSea['Production_Limit_ton_calculated'].notna()]


# # convert all Production Limits to tons
# production_limits_df['Production_Limit_ton_calculated'] = production_limits_df.apply(lambda row: row['LimiteProduccion'] / 1000 if row['UnidadMedidaProduccionId'] == 2 else row['LimiteProduccion'], axis=1)
# # replace Producción with Nan in IdSea
# production_limits_df['IdSea'] = production_limits_df['IdSea'].replace('Producción)', np.nan) # only 10 cases of this
# production_limits_df['IdSea'] = production_limits_df['IdSea'].replace('Biomasa Último Año de', np.nan) # only 9 cases of this
# # remove nan in IdSea
# production_limits_df = production_limits_df[production_limits_df['IdSea'].notna()]
# # convert IdSea to int
# production_limits_df['IdSea'] = production_limits_df['IdSea'].astype(int)

# # rename N_CODIGOCE to Rna in concessions_2024
# concessions_2024 = concessions_2024.rename(columns={'N_CODIGOCE': 'Rna'})
# concessions_2024_lat_long = process_dataframe_coordinates(concessions_2024, 'COORDENADA')


# # concessions_2024 = gpd.read_file('data/concession/from_sma_Approved areas_ccaa_nac_shp_042024/ccaa_nacional.shp')
# concessions_2024 = pd.read_csv('data/concession/concessions_2024_lat_long.csv')
# concessions_2024 = concessions_2024.drop_duplicates()
# concessions_2024 = concessions_2024.rename(columns={'N_CODIGOCE': 'Rna'})
# concessions_2024_lat_long = process_dataframe_coordinates(concessions_2024, 'COORDENADA')
# concessions_2024_lat_long = concessions_2024_lat_long[concessions_2024_lat_long['latitude'].notna()]
# concessions_2024_lat_long = concessions_2024_lat_long[concessions_2024_lat_long['longitude'].notna()]

# ## Complaints Data

# aqua_tipline = pd.read_excel('data/tipline/aquaculture_tips.xlsx')
# aqua_tipline = aqua_tipline.drop_duplicates()


# # open csv as df data/concession/concessions_2024_by_production_streamlit.csv

# production_df = pd.read_csv('data/concession/concessions_2024_by_production_streamlit.csv')
# concessions_2024_by_production_complaints = pd.read_csv('data/concession/concessions_2024_by_production_complaints.csv')

# concessions_2024_by_production_complaints['AGE_OF_CONCESSION (Years)'] = pd.to_datetime('2025-01-01') - pd.to_datetime(concessions_2024_by_production_complaints['F_RESOLSSP'])
# # remove years and convert to float
# concessions_2024_by_production_complaints['AGE_OF_CONCESSION (Years)'] = concessions_2024_by_production_complaints['AGE_OF_CONCESSION (Years)'].dt.days / 365
# # convert to integer
# concessions_2024_by_production_complaints['AGE_OF_CONCESSION (Years)'] = concessions_2024_by_production_complaints['AGE_OF_CONCESSION (Years)'].astype(int)
# # filter for IdSea is Nan
# technical_projects = pd.read_csv('data/concession/technical_projects_2024_streamlit.csv')
# technical_projects['AGE_OF_CONCESSION (Years)'] = pd.to_datetime('2025-01-01') - pd.to_datetime(technical_projects['F_RESOLSSP'])
# # remove years and convert to float
# technical_projects['AGE_OF_CONCESSION (Years)'] = technical_projects['AGE_OF_CONCESSION (Years)'].dt.days / 365
# # convert to integer
# technical_projects['AGE_OF_CONCESSION (Years)'] = technical_projects['AGE_OF_CONCESSION (Years)'].astype(int)
# technical_projects = technical_projects.rename(columns={'Rna': 'Rna_Technical_Projects', 'IdSea': 'IdSea_Technical_Projects', 'Production_Limit_ton_calculated': 'Production_Limit_ton_calculated_Technical_Projects', 'SUPERFICIE': 'SUPERFICIE_Technical_Projects', 'AGE_OF_CONCESSION (Years)': 'AGE_OF_CONCESSION (Years) Technical_Projects', 'TITULAR': 'TITULAR_Technical_Projects', 'REGION': 'REGION_Technical_Projects', 'ComplaintCount': 'ComplaintCount_Technical_Projects'})

# fig = px.scatter(
#     concessions_2024_by_production_complaints,
#     x="Production_Limit_ton_calculated",
#     y="SUPERFICIE",
#     size="ComplaintCount",
#     color="TITULAR",
#     hover_name="TITULAR",
#     log_x=False,
#     size_max=60,
#     hover_data=["Rna", "REGION", "TITULAR", "Production_Limit_ton_calculated", "SUPERFICIE", "ComplaintCount"]
# )

# fig.update_layout(
#         xaxis_range=[-2000, 20000],             # Set x-axis range
#         yaxis_range=[-50, 200])

# fig2 = px.scatter(
#     concessions_2024_by_production_complaints,
#     x="Production_Limit_ton_calculated",
#     y="AGE_OF_CONCESSION (Years)",
#     size="ComplaintCount",
#     color="TITULAR",
#     hover_name="TITULAR",
#     log_x=False,
#     size_max=60,
#     hover_data=["Rna", "REGION", "TITULAR", "Production_Limit_ton_calculated", "AGE_OF_CONCESSION (Years)", "ComplaintCount"]
# )

# fig2.update_layout(
#     xaxis_range=[-2000, 20000],
#     yaxis_range=[-5, 55])

# fig3 = px.scatter(
#     concessions_2024_by_production_complaints,
#     x="Production_Limit_ton_calculated",
#     y="SUPERFICIE",
#     size="ComplaintCount",
#     color="REGION",
#     hover_name="REGION",
#     log_x=False,
#     size_max=60,
#     hover_data=["Rna", "REGION", "TITULAR", "Production_Limit_ton_calculated", "SUPERFICIE", "ComplaintCount"]
# )

# fig3.update_layout(
#     xaxis_range=[-2000, 20000],
#     yaxis_range=[-50, 200])

# fig4 = px.scatter(
#     concessions_2024_by_production_complaints,
#     x="Production_Limit_ton_calculated",
#     y="AGE_OF_CONCESSION (Years)",
#     size="ComplaintCount",
#     color="REGION",
#     hover_name="REGION",
#     log_x=False,
#     size_max=60,
#     hover_data=["Rna", "REGION", "TITULAR", "Production_Limit_ton_calculated", "AGE_OF_CONCESSION (Years)", "ComplaintCount"])

# fig4.update_layout(
#     xaxis_range=[-2000, 20000],
#     yaxis_range=[-5, 55])


# fig5 = px.scatter(
#     technical_projects,
#     x="AGE_OF_CONCESSION (Years) Technical_Projects",
#     y="SUPERFICIE_Technical_Projects",
#     # size="ComplaintCount_Technical_Projects",
#     color="REGION_Technical_Projects",
#     hover_name="REGION_Technical_Projects",
#     log_x=False,
#     size_max=60,
#     hover_data=["Rna_Technical_Projects", "REGION_Technical_Projects", "TITULAR_Technical_Projects", "SUPERFICIE_Technical_Projects", ]
#     )

# fig5.update_layout(
#     xaxis_range=[-5, 55],
#     yaxis_range=[-50, 200])

# fig6 = px.scatter(
#     technical_projects,
#     x="AGE_OF_CONCESSION (Years) Technical_Projects",
#     y="SUPERFICIE_Technical_Projects",
#     # size=,
#     color="T_GRUPOESP",
#     hover_name="T_GRUPOESP",
#     log_x=False,
#     size_max=60,
#     hover_data=["Rna_Technical_Projects", "T_GRUPOESP", "TITULAR_Technical_Projects", "AGE_OF_CONCESSION (Years) Technical_Projects", ])

# fig6.update_layout(
#     xaxis_range=[-5, 55],
#     yaxis_range=[-50, 200])

# fig7 = px.scatter(
#     technical_projects,
#     x="AGE_OF_CONCESSION (Years) Technical_Projects",
#     y="SUPERFICIE_Technical_Projects",
#     # size=,
#     color="TITULAR_Technical_Projects",
#     hover_name="TITULAR_Technical_Projects",
#     log_x=False,
#     size_max=60,
#     hover_data=["Rna_Technical_Projects", "REGION_Technical_Projects", "TITULAR_Technical_Projects","SUPERFICIE_Technical_Projects", ])

# fig7.update_layout(
#     xaxis_range=[-5, 55],
#     yaxis_range=[-50, 200])

# fig8 = px.scatter(
#     technical_projects,
#     x="AGE_OF_CONCESSION (Years) Technical_Projects",
#     y="SUPERFICIE_Technical_Projects",
#     # size=,
#     color="TOPONIMIO",
#     hover_name="TOPONIMIO",
#     log_x=False,
#     size_max=60,
#     hover_data=["Rna_Technical_Projects", "REGION_Technical_Projects", "TITULAR_Technical_Projects", "AGE_OF_CONCESSION (Years) Technical_Projects", "SUPERFICIE_Technical_Projects"])


# fig8.update_layout(
#     xaxis_range=[-5, 55],
#     yaxis_range=[-50, 200])


# st.subheader("Salmons Concessions & Complaints Exploration")

# tab3, tab4 = st.tabs(["Production vs. Surface Area vs. Complaints by Region", "Production vs. Age of Concessions vs. Complaints by Region"])
# with tab3:
#     st.plotly_chart(fig3, theme="streamlit", use_container_width=True)
# with tab4:
#     st.plotly_chart(fig4, theme="streamlit", use_container_width=True)

# tab1, tab2= st.tabs(["Production vs. Surface Area vs. Complaints by Owner", "Production vs. Age of Concessions vs. Complaints by Owner"])
# with tab1:
#     # Use the Streamlit theme.
#     # This is the default. So you can also omit the theme argument.
#     st.plotly_chart(fig, theme="streamlit", use_container_width=True)
# with tab2:
#     # Use the native Plotly theme.
#     st.plotly_chart(fig2, theme="streamlit", use_container_width=True)



# st.subheader("Salmon Technical Projects Exploration")

# tab7, tab8 = st.tabs(["Age of Concession vs. Surface Area by Owner", "Age of Concession vs. Age of Concessions by Toponimio"])
# with tab7:
#     st.plotly_chart(fig7, theme="streamlit", use_container_width=True)
# with tab8:
#     st.plotly_chart(fig8, theme="streamlit", use_container_width=True)


# tab5, tab6= st.tabs(["Age of Concession vs. Surface Area by Region", "Age of Concession vs. Age of Concessions by Species"])
# with tab5:
#     st.plotly_chart(fig5, theme="streamlit", use_container_width=True, key="fig5")
# with tab6:
#     # Use the native Plotly theme.
#     st.plotly_chart(fig6, theme="streamlit", use_container_width=True, key="fig6")

# # st.dataframe(technical_projects)


# st.subheader("Salmon Complaints Normalized by Region")

# # how many Rna per region 
# rna_per_region = concessions_2024_by_production_complaints.groupby('REGION').agg({'Rna': 'count'})
# # change Rna to Rna_Count
# rna_per_region.rename(columns={'Rna': 'Rna_Count'}, inplace=True)

# # left join rna_per_region onto concessions_2024_by_production_complaints on REGION
# concessions_2024_by_production_complaints_rna_per_region = pd.merge(concessions_2024_by_production_complaints, rna_per_region, on='REGION', how='left')

# # st.dataframe(concessions_2024_by_production_complaints_rna_per_region)
# # print(rna_per_region.head())
# # left join rna_per_region onto concessions_2024_by_production_complaints on REGION
# concessions_2024_by_production_complaints_rna_per_region['Normalized_ComplaintCount_per_Rna'] = concessions_2024_by_production_complaints_rna_per_region['ComplaintCount']/concessions_2024_by_production_complaints_rna_per_region['Rna_Count']

# st.bar_chart(concessions_2024_by_production_complaints_rna_per_region, y='Normalized_ComplaintCount_per_Rna', x='REGION', color='REGION', use_container_width=True, height=500)

# # add small, well formated, table of the complaints by region

# st.subheader("Salmon Complaints over Time")

# # plotly line chart of aqua_tipline['DateComplaintSubmission']
# # group by DateComplaintSubmission and count the number of complaints
# aqua_tipline['DateComplaintSubmission'] = pd.to_datetime(aqua_tipline['DateComplaintSubmission'])
# aqua_tipline_grouped = aqua_tipline.groupby('DateComplaintSubmission').size().reset_index(name='ComplaintCount')
# fig4 = px.line(aqua_tipline_grouped, x='DateComplaintSubmission', y='ComplaintCount')
# st.plotly_chart(fig4, theme="streamlit", use_container_width=True)

# # st.subheader("Salmon Concessions Exploration")
# # st.map(concessions_2024_lat_long)


# ######

