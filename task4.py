# -*- coding: utf-8 -*-
"""
Created on Mon Dec 15 15:35:49 2025

@author: User
"""

import pandas as pd
import numpy as np
import pickle as pk
import xarray as xr
import sys
import os
import pandas.core.indexes.base

# ========================================================
# 1. COMPATIBILITY PATCH (Essential for loading files)
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
# Paths
drought_path = r"D:\enviournmental programming\project\data\data\drought.pkl"
heatwaves_path = r"D:\enviournmental programming\project\data\data\heatwaves.pkl"
meta_drought_path = r"D:\enviournmental programming\project\data\data\metadata_drought.pkl"
meta_heat_path = r"D:\enviournmental programming\project\data\data\metadata_heatwaves.pkl"

print("Loading datasets...")

# Load Drought
with open(drought_path, 'rb') as f:
    drought1 = pk.load(f)
with open(meta_drought_path, 'rb') as f:
    drought_meta = pk.load(f)

# Load Heatwaves
with open(heatwaves_path, 'rb') as f:
    heatwaves1 = pk.load(f)

# Load Heatwaves Metadata (with fallback)
if os.path.exists(meta_heat_path):
    with open(meta_heat_path, 'rb') as f:
        heatwaves_meta = pk.load(f)
else:
    # Fallback to generic metadata if specific file missing
    fallback = r"D:\enviournmental programming\project\data\data\metadata.pkl"
    print(f"Warning: {meta_heat_path} not found. Using {fallback}")
    with open(fallback, 'rb') as f:
        heatwaves_meta = pk.load(f)

print("Data loaded. Executing Task 4 logic...")

# ========================================================
# 3. TASK 4 LOGIC 
# ========================================================

# Assuming heatwaves and drought are loaded as dictionaries of xarray Datasets
mode = 'roads'
rcp_target = 'rcp60'  # RCP 6.0

# Helper: get runs for given RCP
def get_runs_for_rcp(rcp, metadata):
    # Ensure strict string matching and handle potential integer/string mismatch
    valid_runs = []
    for run, meta in metadata.items():
        # Check if 'rcp' key exists and matches
        if meta.get('rcp') == rcp:
            valid_runs.append(run)
    return valid_runs

# Select runs for heatwaves and drought
heatwave_runs = get_runs_for_rcp(rcp_target, heatwaves_meta)
drought_runs = get_runs_for_rcp(rcp_target, drought_meta)  # assuming similar structure

print(f"Found {len(heatwave_runs)} heatwave runs and {len(drought_runs)} drought runs for {rcp_target}.")

# Function to create a dataframe: columns = ['year', 'run', 'climate_model', 'extreme', 'exposure']
def create_df(ds, runs, metadata, extreme_name):
    records = []
    for run in runs:
        # Check if run exists in the dataset before accessing
        if run not in ds[mode].run.values:
            continue
            
        # Sum dimensions (Task 2 logic applied here )
        exposure = ds[mode]['exposure'].sel(run=run).sum(dim=['lat','lon']).values
        years = ds[mode]['time'].values
        climate_model = metadata[run]['gcm']
        
        for y, e in zip(years, exposure):
            records.append({
                'year': y,
                'run': run,
                'climate_model': climate_model,
                'extreme': extreme_name,
                'exposure': e
            })
    return pd.DataFrame.from_records(records)

# Create dataframes
df_heatwave = create_df(heatwaves1, heatwave_runs, heatwaves_meta, 'heatwave')
df_drought = create_df(drought1, drought_runs, drought_meta, 'drought')

# Combine
combined_RCP6_Road = pd.concat([df_heatwave, df_drought], ignore_index=True)

# Show the head
print("\nCombined DataFrame Head:")
print(combined_RCP6_Road.head())

# Optional: Inspect a few more rows to verify both extremes are present
print("\nValue Counts for 'extreme':")
print(combined_RCP6_Road['extreme'].value_counts())