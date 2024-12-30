# %%
import growattServer
from dotenv import load_dotenv
import os
import rich

load_dotenv()

api = growattServer.GrowattApi(False, "something")
r = api.login(os.getenv("GROWATT_USER"), os.getenv("GROWATT_PASSWORD"), False)

# %%
plants = api.plant_list(r["user"]["id"])
rich.print(plants)

plant_map = {plant["plantName"]: plant["plantId"] for plant in plants["data"]}

# %%
for plant_name, plant_id in plant_map.items():
    # res = api.device_list(plant_id)
    # rich.print(res)
    print(plant_id, plant_name)
    # res = api.plant_energy_data(plant_id)
    # rich.print(res)
    # res = api.inverter_list(plant_id)

    res = api.plant_info(plant_id)

    rich.print(res)

# %%
