import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pickle as pk
import xarray as xr
import sys
import os
import pandas.core.indexes.base

# ========================================================
# 1. AGGRESSIVE COMPATIBILITY PATCH (The Fix)
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

# ========================================================
# 2. LOAD DATA
# ========================================================
base_path = r"D:\enviournmental programming\project\data\data"
heatwaves_path = os.path.join(base_path, "heatwaves.pkl")
metadata_path = os.path.join(base_path, "metadata_heatwaves.pkl")

# Fallback: if specific metadata file is missing, try generic one
if not os.path.exists(metadata_path):
    metadata_path = os.path.join(base_path, "metadata.pkl")

print("Loading Heatwave Data...")
try:
    with open(heatwaves_path, 'rb') as f:
        heatwaves1 = pk.load(f)
    print("SUCCESS: Loaded heatwaves.pkl")

    with open(metadata_path, 'rb') as f:
        heatwaves_meta = pk.load(f)
    print("SUCCESS: Loaded metadata.")
except FileNotFoundError:
    print("Error: Files not found. Check your paths!")
    raise

# ========================================================
# 3. PREPARE METADATA
# ========================================================
# Convert metadata to DataFrame for easier filtering
meta_df = pd.DataFrame.from_dict(heatwaves_meta, orient="index")
meta_df["run"] = meta_df.index.astype(int)

# Normalize RCP names (just in case they vary in the file)
if "rcp" in meta_df.columns:
    # Ensure they look like 'rcp26', 'rcp60', etc.
    meta_df["rcp"] = meta_df["rcp"].astype(str).str.lower().str.replace(r"[^\d]", "", regex=True)
    meta_df["rcp"] = meta_df["rcp"].apply(lambda s: f"rcp{s}" if s and not s.startswith("rcp") else s)

# ========================================================
# 4. PLOTTING FUNCTION (Task 2 Logic)
# ========================================================
def plot_exposure_timeseries(mode_name, ds, rcp):
    """
    Plots the time series of exposure for a specific mode and RCP.
    Includes one line per Climate Model (GCM).
    """
    print(f"  Plotting {mode_name} for {rcp}...")
    
    # 1. Select runs belonging to this RCP
    rcp_runs = meta_df.loc[meta_df["rcp"] == rcp, "run"].values
    
    if len(rcp_runs) == 0:
        print(f"    Warning: No runs found for {rcp}")
        return

    # 2. Group runs by climate model (GCM)
    # This creates a dictionary: {'gfdl-esm2m': [1, 2], 'miroc5': [3, 4], ...}
    # We filter first to ensure we only group runs that belong to this RCP
    relevant_meta = meta_df[meta_df["run"].isin(rcp_runs)]
    
    if "gcm" in relevant_meta.columns:
        gcm_col = "gcm" 
    else: 
        gcm_col = "model" # Fallback if column name is different

    gcm_groups = relevant_meta.groupby(gcm_col)["run"].apply(list)
    
    plt.figure(figsize=(10, 6))
    
    # 3. Loop through each climate model to plot its line
    found_data = False
    for gcm, runs in gcm_groups.items():
        # Only select runs that actually exist in the dataset
        valid_runs = [r for r in runs if r in ds.run.values]
        
        if not valid_runs:
            continue
            
        found_data = True
        ds_gcm = ds.sel(run=valid_runs)

        # ---- MATHEMATICAL STEP ----
        # "Sum for each year, the exposure values over Europe"
        # .sum(dim=['lat', 'lon']) collapses the map into a single number per year
        spatial_sum = ds_gcm["exposure"].sum(dim=["lat", "lon"])

        # "Average across runs belonging to this GCM" (if a model has multiple runs)
        gcm_timeseries = spatial_sum.mean(dim="run")

        # Plot
        try:
            x_vals = ds_gcm.time.values
        except:
            x_vals = np.arange(len(gcm_timeseries))

        plt.plot(x_vals, gcm_timeseries, label=gcm, linewidth=2)

    if not found_data:
        print(f"    No valid data found for {mode_name} in {rcp}")
        plt.close()
        return

    plt.title(f"Heatwave Exposure: {mode_name.upper()} ({rcp.upper()})")
    plt.xlabel("Year")
    plt.ylabel("Total Exposure (Summed over Europe)")
    plt.legend(title="Climate Model")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

# ========================================================
# 5. MAIN LOOP
# ========================================================
transport_modes = list(heatwaves1.keys())[:5] # Limit to first 5 modes (Roads, Rail, etc.)
RCPs = ["rcp26", "rcp60", "rcp85"]

print("\n--- Starting Plot Generation ---")
for rcp in RCPs:
    print(f"\nProcessing {rcp}...")
    for mode in transport_modes:
        ds_mode = heatwaves1[mode]
        plot_exposure_timeseries(mode, ds_mode, rcp)

print("\nTask 2 Complete.")