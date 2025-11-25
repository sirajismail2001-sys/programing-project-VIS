# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 11:43:43 2025

@Siraj: User
"""
import pickle as pk
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr

# ---------------- PATH ----------------
data_path = r"D:\enviournmental programming\project\data\data"

# ---------------- LOAD PKL FILES ----------------
with open(fr"{data_path}\drought.pkl", "rb") as f:
    drought = pk.load(f)

with open(fr"{data_path}\metadata_drought.pkl", "rb") as f:
    meta = pk.load(f)

# Transport modes
transport_modes = drought.coords["mode"].values
RCP_list = ["rcp26", "rcp60", "rcp85"]

# ------------- TASK 1 LOOP -------------
for rcp in RCP_list:

    # Select runs belonging to this RCP
    rcp_runs = [i for i, info in meta.items() if info["rcp"] == rcp]

    data_rcp = drought.sel(run=rcp_runs)
    data_2050_2099 = data_rcp.sel(year=slice(2050, 2099))

    # Mean over years and runs
    mean_exposure = data_2050_2099.mean(dim=["year", "run"])

    # ----- Plot per mode -----
    for mode in transport_modes:
        plt.figure(figsize=(8, 5))
        plt.title(f"Mean Drought Exposure | Mode: {mode} | {rcp}")
        plt.imshow(mean_exposure.sel(mode=mode), origin="lower")
        plt.colorbar(label="Mean exposure")
        plt.tight_layout()
        plt.show()
