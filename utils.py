import growattServer
from dotenv import load_dotenv
import os
import datetime
import pandas as pd

load_dotenv()

api = growattServer.GrowattApi(False, "something")
login_response = api.login(
    os.getenv("GROWATT_USER"), os.getenv("GROWATT_PASSWORD"), False
)


def get_plant_id_map() -> dict:
    r = api.plant_list(login_response["user"]["id"])
    plant_map = dict()
    for plant_data in r["data"]:
        plant_id = plant_data["plantId"]
        plant_name = plant_data["plantName"]
        plant_map[plant_name] = dict(plant_id=plant_id, plant_name=plant_name)
    return plant_map


def get_a_plants_current_power(plant_id: str) -> dict:
    res = api.plant_info(plant_id)

    if inverter_list := res.get("invList"):
        power_sum = 0
        for inverter in inverter_list:
            power_sum += float(inverter.get("power", 0))
        return power_sum

    else:
        return float(res.get("nominalPower"))


def get_current_total_sysOut(plant_map: dict) -> pd.DataFrame:
    total_sysOut = 0
    for plant_data in plant_map.values():
        plant_id = plant_data["plant_id"]
        res = api.dashboard_data(plant_id, timespan=growattServer.Timespan["hour"])
        chart_data = res["chartData"]
        if chart_data == dict():
            continue
        latest_time_key = max(
            chart_data.keys(),
            key=lambda x: datetime.datetime.strptime(x, "%H:%M").time(),
        )
        total_sysOut += float(chart_data[latest_time_key].get("sysOut", 0))

    return pd.DataFrame(
        {
            "Column 1": ["Netzbezug", "Hausverbrauch"],
            "Leistng [kW]": [total_sysOut, 0.0],
        }
    )


def get_a_plants_today_power(plant_id: str) -> float:

    res = api.dashboard_data(plant_id, timespan=growattServer.Timespan["day"])
    chart_data = res["chartData"]
    if not chart_data:
        return 0

    if len(chart_data["ppv"]) > 0:
        return float(chart_data["ppv"][-1])
    return 0.0


def get_a_plants_current_months_power(plant_id: str) -> float:

    res = api.plant_energy_data(plant_id)
    month_power = float(res.get("monthValue", 0))
    return month_power


def get_total_current_power(plant_map: dict) -> float:
    total_power = 0
    for plant_data in plant_map.values():
        plant_id = plant_data["plant_id"]
        power = get_a_plants_current_power(plant_id)
        total_power += power
    return total_power


def get_todays_power(plant_map: dict) -> float:
    total_power = 0
    for plant_data in plant_map.values():
        res = api.plant_info(plant_data["plant_id"])
        total_power += float(res.get("todayEnergy", 0))
    return total_power


def get_this_months_power(plant_map: dict) -> float:
    total_power = 0
    for plant_data in plant_map.values():
        plant_id = plant_data["plant_id"]
        power = get_a_plants_current_months_power(plant_id)
        total_power += power
    return total_power


def get_total_power_production(plant_map: dict) -> float:
    total_power = 0
    for plant_data in plant_map.values():
        plant_id = plant_data["plant_id"]
        res = api.plant_info(plant_id)
        total_power += float(res.get("totalEnergy", 0))
    return total_power


def get_overview_dataframe() -> pd.DataFrame:
    plant_map = get_plant_id_map()
    total_power = get_total_power_production(plant_map)
    months_power = get_this_months_power(plant_map)
    todays_power = get_todays_power(plant_map)
    df = pd.DataFrame(
        {
            "Zeitraum": ["Heute", "Monat", "Gesamt"],
            "Leistung kW/h": [todays_power, months_power, total_power],
        }
    )

    return df


def get_current_plant_powers(plant_map: dict) -> pd.DataFrame:
    plant_names = []
    plant_powers = []

    for plant_data in plant_map.values():
        plant_id = plant_data["plant_id"]
        plant_name = plant_data["plant_name"]
        plant_names.append(plant_name)
        plant_powers.append(get_a_plants_current_power(plant_id))

    plant_names.append("Gesamt")
    total_power = sum(plant_powers)
    plant_powers.append(total_power)
    return pd.DataFrame(
        {
            "Wechselrichter": plant_names,
            "Leistung [W]": plant_powers,
        }
    )


def get_storage_info_df(plant_map: dict) -> list[pd.DataFrame]:
    storage_dfs = list()

    storage_idx = 1
    for plant_data in plant_map.values():
        plant_id = plant_data["plant_id"]
        res = api.plant_info(plant_id)

        if storage_list := res.get("storageList"):

            for storage in storage_list:
                capacity = storage.get("capacity", 0)
                p_charge = storage.get("pCharge", 0)
                df = pd.DataFrame(
                    {
                        f"Speicher {storage_idx}": ["Kapazität", "Ladeleistung [W]"],
                        "Wert": [capacity, p_charge],
                    }
                )
                storage_dfs.append(df)
    return storage_dfs
