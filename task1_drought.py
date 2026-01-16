

import matplotlib.pyplot as plt
import pandas as pd
import pickle as pk
import sys
import pandas.core.indexes.base

# ========================================================
# 1. COMPATIBILITY PATCH (Prevents Loading Errors)
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
#####task 1#####
# ========================================================
# 2. LOAD DATA FROM  PATHS
# ========================================================
# Define your specific file paths
drought_path = r"D:\enviournmental programming\project\data\data\drought.pkl"
metadata_path = r"D:\enviournmental programming\project\data\data\metadata_drought.pkl"

print("Loading data...")

# Load the main drought data
with open(drought_path, 'rb') as f:
    drought1 = pk.load(f)  # Loading into variable 'drought1' to match your code

# Load the metadata
with open(metadata_path, 'rb') as f:
    drought_meta = pk.load(f) # Loading into variable 'drought_meta'

print("Data loaded successfully. Starting plots...")

# ========================================================
# 3. YOUR PLOTTING CODE
# ========================================================

transport_modes = list(drought1.keys())[:5]
RCPs = ["rcp26", "rcp60", "rcp85"]

# Convert metadata into DataFrame
meta_df = pd.DataFrame.from_dict(drought_meta, orient="index")
meta_df["run"] = meta_df.index.astype(int)

# Time window
start_year = 2050
end_year = 2099

# ===================== LOOP OVER TRANSPORT MODES =====================
for mode in transport_modes:

    print(f"\n=== Plotting mode: {mode} ===")

    # Create figure: 1 row × 3 columns (one for each RCP)
    fig, axes = plt.subplots(
        nrows=1,
        ncols=len(RCPs),
        figsize=(18, 6),
        constrained_layout=True
    )

    # Access our dataset for this transport mode
    ds_mode = drought1[mode]

    # Loop over RCPs
    for i, rcp in enumerate(RCPs):

        # ---- Select runs belonging to this RCP ----
        # Filter rows where rcp matches, then get 'run' column values
        rcp_runs = meta_df.loc[meta_df["rcp"] == rcp, "run"].values
        
        # Only select runs that actually exist in this dataset to avoid errors
        valid_runs = [r for r in rcp_runs if r in ds_mode.run.values]
        
        if not valid_runs:
            print(f"Warning: No valid runs found for {mode} in {rcp}")
            continue

        ds_rcp = ds_mode.sel(run=valid_runs)

        # ---- Select 2050–2099 ----
        ds_period = ds_rcp.sel(time=slice(start_year, end_year))

        # ---- Average across time and run ----
        mean_exposure = ds_period["exposure"].mean(dim=["run", "time"])

        # ---- Plot map ----
        ax = axes[i]

        mean_exposure.plot(
            ax=ax,
            cmap="Reds",
            cbar_kwargs={"label": "Mean Exposure (2050–2099)"}
        )

        # Titles & labels
        ax.set_title(f"{mode} – {rcp.upper()}")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")

    # Figure title for this transport mode
    fig.suptitle(f"{mode} – Mean Exposure Maps (2050–2099)", fontsize=16)

    plt.show()
    


