###task 8 for ratios

import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import pickle as pk
import pandas as pd
import sys
import os
import pandas.core.indexes.base

# ========================================================
# 1. COMPATIBILITY PATCH & IMPORTS
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
# 2. LOAD DATA (Using your paths)
# ========================================================
drought_path = r"D:\enviournmental programming\project\data\data\drought.pkl"
heatwaves_path = r"D:\enviournmental programming\project\data\data\heatwaves.pkl"
meta_drought_path = r"D:\enviournmental programming\project\data\data\metadata_drought.pkl"
meta_heat_path = r"D:\enviournmental programming\project\data\data\metadata_heatwaves.pkl"

# Fallback for metadata
if not os.path.exists(meta_heat_path):
    meta_heat_path = r"D:\enviournmental programming\project\data\data\metadata.pkl"

print("Loading data for Task 8...")
with open(drought_path, 'rb') as f:
    drought1 = pk.load(f)
with open(meta_drought_path, 'rb') as f:
    drought_meta = pk.load(f)
with open(heatwaves_path, 'rb') as f:
    heatwaves1 = pk.load(f)
with open(meta_heat_path, 'rb') as f:
    heatwaves_meta = pk.load(f)

# ========================================================
# 3. SETTINGS & DEFINITIONS
# ========================================================
mode = 'roads'
rcp_target = 'rcp60'

# Periods as per assignment
periods = {
    "past": (1861, 1890),
    "present": (1981, 2010),
    "future1": (2041, 2070),
    "future2": (2071, 2099)
}

# --- Helper Functions ---
def get_runs_for_rcp(rcp, metadata):
    return [run for run, meta in metadata.items() if meta.get('rcp') == rcp]

#  FUNCTION: Boolean Logic (> 0.5) 
def compound_occurrence(extreme1: xr.DataArray, extreme2: xr.DataArray) -> xr.DataArray:
    # Safety Check: Align coordinates if needed
    if extreme1.shape != extreme2.shape:
        extreme2['lat'] = extreme1['lat']
        extreme2['lon'] = extreme1['lon']
    
    # --- NOTEBOOK LOGIC HERE ---
    # Using Boolean & operator for element-wise comparison
    condition = (extreme1 > 0.5) & (extreme2 > 0.5)
    
    # Return 1 where both are True, else 0
    return xr.where(condition, 1, 0)

# ========================================================
# 4. DATA PREPARATION (Model Alignment)
# ========================================================
heatwave_runs = get_runs_for_rcp(rcp_target, heatwaves_meta)
drought_runs = get_runs_for_rcp(rcp_target, drought_meta)

# Map model names to Run IDs to find common models
heat_model_map = {heatwaves_meta[r]['gcm']: r for r in heatwave_runs}
drought_model_map = {drought_meta[r]['gcm']: r for r in drought_runs}

# Find intersection (Models present in BOTH datasets)
common_models = sorted(list(set(heat_model_map.keys()).intersection(drought_model_map.keys())))

# ========================================================
# 5. CALCULATION LOOP
# ========================================================
res_f1_vs_present = {}
res_f2_vs_present = {}
res_f1_vs_past = {}
res_f2_vs_past = {}

print(f"Task 8: Calculating Ratios for {len(common_models)} models...")

for model in common_models:
    run_h = heat_model_map[model]
    run_d = drought_model_map[model]
    
    # 1. Select Exposure Data
    heatwave_data = heatwaves1[mode]['exposure'].sel(run=run_h)
    drought_data = drought1[mode]['exposure'].sel(run=run_d)
    
    # 2. Compute Compound Coefficient (Using Boolean Logic)
    compound_coeff = compound_occurrence(heatwave_data, drought_data)
    
    # 3. Aggregate Spatially over Europe (Sum of affected grid cells)
    freq_over_europe = compound_coeff.sum(dim=['lat', 'lon'])
    
    # 4. Calculate Mean Frequency for each period
    period_means = {}
    for key, (start, end) in periods.items():
        # Slice the specific years and calculate the average
        p_data = freq_over_europe.sel(time=slice(start, end))
        period_means[key] = p_data.mean().item()
    
    # 5. Calculate Ratios (Future / Baseline)
    # --- VS PRESENT ---
    if period_means["present"] != 0:
        res_f1_vs_present[model] = (period_means["future1"] / period_means["present"])
        res_f2_vs_present[model] = (period_means["future2"] / period_means["present"])
    else:
        # Avoid Division by Zero
        res_f1_vs_present[model] = np.nan
        res_f2_vs_present[model] = np.nan
        
    # --- VS PAST ---
    if period_means["past"] != 0:
        res_f1_vs_past[model] = (period_means["future1"] / period_means["past"])
        res_f2_vs_past[model] = (period_means["future2"] / period_means["past"])
    else:
        res_f1_vs_past[model] = np.nan
        res_f2_vs_past[model] = np.nan

# ========================================================
# 6. EXTRACT & PRINT MEAN VALUES (RATIOS)
# ========================================================
# Use np.nanmean to safely ignore models with 0 baseline events
mean_f1_pres = np.nanmean(list(res_f1_vs_present.values()))
mean_f2_pres = np.nanmean(list(res_f2_vs_present.values()))
mean_f1_past = np.nanmean(list(res_f1_vs_past.values()))
mean_f2_past = np.nanmean(list(res_f2_vs_past.values()))

print("\n" + "="*60)
print("TASK 8 RESULTS: Mean Synchronization Ratios (Factor of Change)")
print("1.0 = No Change. 2.0 = 2x increase.")
print("="*60)
print(f"Future 1 (2041-2070) vs Present: {mean_f1_pres:.2f}x")
print(f"Future 2 (2071-2099) vs Present: {mean_f2_pres:.2f}x")
print("-" * 60)
print(f"Future 1 (2041-2070) vs Past:    {mean_f1_past:.2f}x")
print(f"Future 2 (2071-2099) vs Past:    {mean_f2_past:.2f}x")
print("="*60 + "\n")

# ========================================================
# 7. PLOTTING (RATIO COMPARISON)
# ========================================================
print("Generating Plot...")

# Sort models for consistent plotting
climate_models_sorted = sorted(common_models)

# Use Raw Ratios for plotting
data_pres = [res_f2_vs_present[cm] for cm in climate_models_sorted]
data_past = [res_f2_vs_past[cm] for cm in climate_models_sorted]

# Add Means to the end of the list
labels = climate_models_sorted + ["MEAN"]
data_pres.append(mean_f2_pres)
data_past.append(mean_f2_past)

# X-axis setup
x = np.arange(len(labels))
width = 0.35

fig, ax = plt.subplots(figsize=(14, 7))

# Draw Bars
rects1 = ax.bar(x - width/2, data_pres, width, label='Future 2 (2071-2099) vs Present', color='skyblue')
rects2 = ax.bar(x + width/2, data_past, width, label='Future 2 (2071-2099) vs Past', color='salmon')

# Labels and Titles
ax.set_ylabel('Ratio of Change (Future / Baseline)')
ax.set_title(f'End-of-Century Synchronization Factor ({mode.capitalize()}, {rcp_target.upper()})\n(Ratio > 1 means increase)', fontsize=14)
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=45, ha='right')
ax.legend()
ax.grid(True, axis='y', linestyle='--', alpha=0.7)

# Reference Line at 1.0 (No Change)
ax.axhline(1.0, color='black', linewidth=1.5, linestyle='-', label="Baseline (Ratio=1.0)")

plt.tight_layout()
plt.show()

print("Task 8 Complete.")
