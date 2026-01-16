

import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import pickle as pk
import pandas as pd
import sys
import os
import pandas.core.indexes.base

# ========================================================
# 1. COMPATIBILITY PATCH (Essential for Spyder/Pandas)
# ========================================================
# This fixes the "Int64Index" error common in newer Pandas versions
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

# File Paths
drought_path = os.path.join(base_path, "drought.pkl")
heatwaves_path = os.path.join(base_path, "heatwaves.pkl")
meta_drought_path = os.path.join(base_path, "metadata_drought.pkl")
meta_heat_path = os.path.join(base_path, "metadata_heatwaves.pkl")

# Metadata Fallback
if not os.path.exists(meta_heat_path):
    meta_heat_path = os.path.join(base_path, "metadata.pkl")

print("Loading data...")

# Load Drought
with open(drought_path, 'rb') as f:
    drought1 = pk.load(f)
with open(meta_drought_path, 'rb') as f:
    drought_meta = pk.load(f)

# Load Heatwaves
with open(heatwaves_path, 'rb') as f:
    heatwaves1 = pk.load(f)
with open(meta_heat_path, 'rb') as f:
    heatwaves_meta = pk.load(f)

print("Data Loaded successfully.")

# ========================================================
# 3. TASK 5: COMPOUND EVENT FUNCTION & DATA PREP
# ========================================================
print("Executing Task 5 (Compound Function)...")

# 1. Select Target: Roads and RCP 6.0
target_mode = 'roads'
target_rcp = 'rcp60'

# 2. Identify common runs for RCP 6.0 in both datasets
# (Using Jupyter Notebook logic: simple set intersection of Run IDs)
drought_runs_60 = [k for k, v in drought_meta.items() if v['rcp'] == target_rcp]
heat_runs_60 = [k for k, v in heatwaves_meta.items() if v['rcp'] == target_rcp]
common_runs = list(set(drought_runs_60) & set(heat_runs_60))

print(f"Analyzing {target_mode} under {target_rcp}. Found {len(common_runs)} matching climate models.")

# 3. Define the Compound Function (User's Boolean Logic)
def compound_occurrence(extreme1, extreme2):
    """
    Identifies synchronized events using boolean logic.
    Returns 1 if both extremes are active (> 0.5), else 0.
    """
    # Align coordinates if they differ slightly (Safety check)
    # This prevents errors if lat/lon are off by tiny amounts
    if extreme1.shape != extreme2.shape:
        # Note: This forces alignment. Only do this if you are sure grids are identical.
        extreme2['lat'] = extreme1['lat']
        extreme2['lon'] = extreme1['lon']
    
    # Check if BOTH events are greater than 0.5 simultaneously
    # Since data is binary (0 or 1), > 0.5 is equivalent to == 1
    condition = (extreme1 > 0.5) & (extreme2 > 0.5)
    
    # Convert True/False to 1/0
    return xr.where(condition, 1, 0)

print("Task 5 Function Defined (Boolean Logic).")

# ========================================================
# 4. TASK 6: TIME SERIES OF COMPOUND EVENTS
# ========================================================
print("Executing Task 6 (Time Series)...")

plt.figure(figsize=(12, 6))

# Store results for Task 7 (if needed later)
compound_store = {}

for run in common_runs:
    gcm = heatwaves_meta[run]['gcm']
    
    # Select data
    ds_h = heatwaves1[target_mode]['exposure'].sel(run=run)
    ds_d = drought1[target_mode]['exposure'].sel(run=run)
    
    # Apply YOUR function
    compound_map = compound_occurrence(ds_h, ds_d)
    compound_store[run] = compound_map # Save for next task
    
    # Sum over Europe (lat, lon)
    spatial_sum = compound_map.sum(dim=['lat', 'lon'])
    
    # Plot
    spatial_sum.plot(label=gcm, linewidth=1.5)

plt.title(f"Task 6: Compound Events (Roads, RCP 6.0)", fontsize=14)
plt.ylabel("Total Synchronized Events")
plt.legend(title="Climate Model")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

print("Task 5 and 6 Complete.")