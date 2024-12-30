import pandas as pd
import plotly.express as px
import streamlit as st
import utils
import datetime

# Mock data for the tables
data_left_row1 = {"Column 1": ["Row 1", "Row 2"], "Column 2": ["A", "B"]}
data_left_row2 = {"Column 1": ["Row 1", "Row 2"], "Column 2": ["C", "D"]}

plant_map = utils.get_plant_id_map()

# Create dataframes
df_left_row1 = pd.DataFrame(data_left_row1)
df_left_row2 = pd.DataFrame(data_left_row2)
df = utils.get_current_total_sysOut(plant_map)
df_right_row2 = pd.DataFrame(df.set_index(df.columns[0]))

# Sidebar with a refresh button
# if st.sidebar.button("Refresh App"):
#     st.experimental_rerun()

# Create two columns
col1, col2 = st.columns(2)

# First row: Tables in both columns
with col1:
    st.write("Übersicht")
    df = utils.get_overview_dataframe()
    st.table(df.set_index(df.columns[0]))

with col2:
    st.write("Wechselrichter (aktuell)")
    df = utils.get_current_plant_powers(plant_map)
    st.table(df.set_index(df.columns[0]))


# Second row: Tables in both columns
storage_dfs = utils.get_storage_info_df(plant_map)
with col1:
    st.write("Speichersysteme:")
    for idx, df in enumerate(storage_dfs):
        st.write(f"Sepeicher {idx + 1}")
        st.table(df.set_index(df.columns[0]))
with col2:
    st.write("Stromnetz:")
    st.table(df_right_row2)

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
