import pandas as pd
import plotly.express as px
import streamlit as st
import utils
import datetime

total_progress = st.progress(0)
# get data(frames)
plant_map = utils.get_plant_id_map()
total_progress.progress(20)

# Sidebar with a refresh button
# if st.sidebar.button("Refresh App"):
#     st.experimental_rerun()

# Create two columns
col1, col2 = st.columns(2)

# First row: Tables in both columns
with col1:
    st.write("Übersicht")
    df = utils.get_overview_dataframe()
    total_progress.progress(40)
    st.table(df.set_index(df.columns[0]))

with col2:
    st.write("Wechselrichter (aktuell)")
    df = utils.get_current_plant_powers(plant_map)
    total_progress.progress(60)
    st.table(df.set_index(df.columns[0]))


# Second row: Tables in both columns
storage_dfs = utils.get_storage_info_df(plant_map)
total_progress.progress(80)
with col1:
    st.write("Speichersysteme:")
    for idx, df in enumerate(storage_dfs):
        st.write(f"Sepeicher {idx + 1}")
        st.table(df.set_index(df.columns[0]))

with col2:
    st.write("Stromnetz:")
    df = utils.get_current_total_sysOut(plant_map)
    total_progress.progress(100)
    st.table(df.set_index(df.columns[0]))

# Footer with the current datetime
st.markdown(
    """
    <hr style="margin-top: 50px; margin-bottom: 10px;">
    <div style="text-align: center; font-size: 12px; color: gray;">
        Last updated: {current_time}
    </div>
    """.format(
        current_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ),
    unsafe_allow_html=True,
)
