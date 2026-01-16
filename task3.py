

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pickle as pk
import xarray as xr
import sys
import os
import pandas.core.indexes.base

# ========================================================
# 1. COMPATIBILITY PATCH
# ========================================================
sys.modules['pandas.core.indexes.numeric'] = pandas.core.indexes.base
if not hasattr(pandas.core.indexes.base, 'Int64Index'):
    pandas.core.indexes.base.Int64Index = pd.Index
if not hasattr(pandas.core.indexes.base, 'Float64Index'):
    pandas.core.indexes.base.Float64Index = pd.Index
if not hasattr(pd, 'Int64Index'):
    pd.Int64Index = pd.Index
if not hasattr(pd, 'Float64Index'):
    pd.Float64Index = pd.Index

# ========================================================
# 2. LOAD DATA
# ========================================================
base_path = r"D:\enviournmental programming\project\data\data"
heatwaves_path = os.path.join(base_path, "heatwaves.pkl")
metadata_path = os.path.join(base_path, "metadata_heatwaves.pkl")

# Fallback for metadata path
if not os.path.exists(metadata_path):
    metadata_path = os.path.join(base_path, "metadata.pkl")

print("Loading data for Task 3...")
with open(heatwaves_path, 'rb') as f:
    heatwaves1 = pk.load(f)
with open(metadata_path, 'rb') as f:
    heatwaves_meta = pk.load(f)

# ========================================================
# 3. TASK 3: MEDIAN EXPOSURE CALCULATION
# ========================================================
transport_modes = list(heatwaves1.keys())[:5]
RCPs = ["rcp26", "rcp60", "rcp85"]

# Convert metadata to DataFrame
meta_df = pd.DataFrame.from_dict(heatwaves_meta, orient="index")
meta_df["run"] = meta_df.index.astype(int)

# Create figure with 5 subplots (one per mode)
fig, axes = plt.subplots(
    nrows=len(transport_modes),
    ncols=1,
    figsize=(10, 15), # Adjusted size for better report visibility
    sharex=True,
    constrained_layout=True
)

if len(transport_modes) == 1:
    axes = [axes]

for ax, mode in zip(axes, transport_modes):

    ds_mode = heatwaves1[mode]

    for rcp in RCPs:

        # 1. Get runs belonging to this RCP
        rcp_runs = meta_df[meta_df["rcp"] == rcp]["run"].values
        
        # Filter for valid runs only
        valid_runs = [r for r in rcp_runs if r in ds_mode.run.values]
        
        if not valid_runs:
            continue

        # 2. Select dataset for these runs
        ds_rcp = ds_mode.sel(run=valid_runs)

        # 3. SPATIAL mean (Matches Task 2 logic)
        # "mean for each year, the exposure values over Europe"
        spatial_total = ds_rcp["exposure"].mean(dim=["lat", "lon"])

        # 4. MEDIAN ACROSS MODELS (Task 3 Logic)
        # "Calculate the median... across all climate models"
        median_ts = spatial_total.median(dim="run")

        # 5. Plot
        ax.plot(
            median_ts["time"].values,
            median_ts.values,
            label=rcp.upper(),
            linewidth=2
        )

    ax.set_title(f"Transport Mode: {mode.upper()}", fontsize=12)
    ax.set_ylabel("Median Exposure (Summed)")
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()

axes[-1].set_xlabel("Year")

fig.suptitle(
    "Median Heatwave Exposure Over Time\n(Median of 4 Climate Models)",
    fontsize=16
)

plt.show()