# %%
import growattServer
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

api = growattServer.GrowattApi(False, "something")
login_response = api.login(
    os.getenv("GROWATT_USER"), os.getenv("GROWATT_PASSWORD"), False
)

r = api.plant_list(login_response["user"]["id"])


# Function to convert dict to DataFrame
def dict_to_dataframe(datastream):
    df = pd.DataFrame.from_dict(datastream, orient="index")
    df.index.name = "Time"
    df.reset_index(inplace=True)
    return df


def get_last_values(dataframe, name):

    last_row = dataframe.iloc[-1]
    return {
        "Datastream": name,
        "Timestamp": last_row["Time"],
        **last_row.drop("Time").to_dict(),
    }


data_map = dict()
summary_data = list()
for plant_data in r.get("data"):
    plant_name = plant_data.get("plantName")
    plant_id = plant_data.get("plantId")

    r = api.dashboard_data(plant_id, timespan=growattServer.Timespan["hour"])
    chart_data = dict_to_dataframe(r.get("chartData"))
    data_map[plant_name] = chart_data

    if not chart_data.empty:
        summary_data.append(get_last_values(chart_data, plant_name))


summary_df = pd.DataFrame(summary_data)

# Streamlit App
st.title("Inverter Visualization")

# Display summary table
st.subheader("Latest Values from All Datastreams")
st.dataframe(summary_df)


# Sidebar for selecting datastream
option = st.sidebar.selectbox(
    "Select a inverter to visualize:",
    [x for x in data_map.keys()],
)

# Display data and interactive chart
selected_data = data_map[option]
st.subheader(option)
st.dataframe(selected_data)

# Interactive Plotly Line Chart
fig = px.line(
    selected_data,
    x="Time",
    y=["pacToUser", "ppv", "sysOut", "userLoad"],
    labels={"value": "Value", "variable": "Metric"},
    title=f"{option} - Metrics Over Time",
)

# Update layout for better readability
fig.update_layout(
    xaxis_title="Time",
    yaxis_title="Values",
    legend_title="Metrics",
    template="plotly_dark",
)

st.plotly_chart(fig)
