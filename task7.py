import matplotlib.pyplot as plt
import xarray as xr
import pickle as pk
import pandas as pd
import sys
import os

# ========================================================
# 1. SETUP & LOADING (Fixes NameError)
# ========================================================
# --- Boilerplate for pandas compatibility ---
sys.modules['pandas.core.indexes.numeric'] = pd.core.indexes.base
if not hasattr(pd.core.indexes.base, 'Int64Index'):
    pd.core.indexes.base.Int64Index = pd.Index
if not hasattr(pd.core.indexes.base, 'Float64Index'):
    pd.core.indexes.base.Float64Index = pd.Index
if not hasattr(pd, 'Int64Index'):
    pd.Int64Index = pd.Index
if not hasattr(pd, 'Float64Index'):
    pd.Float64Index = pd.Index

# --- Paths (Update if needed) ---
drought_path = r"D:\enviournmental programming\project\data\data\drought.pkl"
heatwaves_path = r"D:\enviournmental programming\project\data\data\heatwaves.pkl"
meta_drought_path = r"D:\enviournmental programming\project\data\data\metadata_drought.pkl"
meta_heat_path = r"D:\enviournmental programming\project\data\data\metadata_heatwaves.pkl"

# Fallback check for metadata path
if not os.path.exists(meta_heat_path):
    meta_heat_path = r"D:\enviournmental programming\project\data\data\metadata.pkl"

print("Loading data... (This may take a moment)")
with open(drought_path, 'rb') as f: drought1 = pk.load(f)
with open(meta_drought_path, 'rb') as f: drought_meta = pk.load(f)
with open(heatwaves_path, 'rb') as f: heatwaves1 = pk.load(f)
with open(meta_heat_path, 'rb') as f: heatwaves_meta = pk.load(f)

# ========================================================
# 2. SETTINGS & DEFINITIONS
# ========================================================
mode = 'roads'
rcp_target = 'rcp60'

# Define all analysis periods
analysis_periods = {
    "Past": (1971, 2000),
    "Present": (2001, 2030),
    "Future 1": (2041, 2070),
    "Future 2": (2071, 2099)
}
period_order = ["Past", "Present", "Future 1", "Future 2"]

# --- Helper Functions ---
def get_runs_for_rcp(rcp, metadata):
    return [run for run, meta in metadata.items() if meta.get('rcp') == rcp]

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


# Get Runs & Common Models
heatwave_runs = get_runs_for_rcp(rcp_target, heatwaves_meta)
drought_runs = get_runs_for_rcp(rcp_target, drought_meta)

# Map model names to run IDs
heat_model_map = {heatwaves_meta[r]['gcm']: r for r in heatwave_runs}
drought_model_map = {drought_meta[r]['gcm']: r for r in drought_runs}

# Find models common to both hazards
common_models = sorted(list(set(heat_model_map.keys()).intersection(drought_model_map.keys())))

# ========================================================
# 3. PLOTTING LOOP (Iterate by Period First)
# ========================================================
print(f"Generating evolutionary plots for {mode} ({rcp_target})...")

for p_name in period_order:
    start_yr, end_yr = analysis_periods[p_name]
    print(f"Processing Period: {p_name} ({start_yr}-{end_yr})")

    # Initialize One Figure per Period (with 4 subplots for the models)
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    for idx, model in enumerate(common_models):
        if idx >= len(axes): break 
        
        ax = axes[idx]
        run_h = heat_model_map[model]
        run_d = drought_model_map[model]
        
        # 1. Select Data
        heatwave_data = heatwaves1[mode]['exposure'].sel(run=run_h)
        drought_data = drought1[mode]['exposure'].sel(run=run_d)
        
        # 2. Calculate Compound Events
        compound_coeff = compound_occurrence(heatwave_data, drought_data)
        
        try:
            # 3. Slice the specific time period
            period_data = compound_coeff.sel(time=slice(start_yr, end_yr))
            
            if len(period_data['time']) > 0:
                # 4. Calculate Frequency
                freq = period_data.sum(dim='time') / len(period_data['time'])
                freq_masked = freq.where(freq > 0)
                
                # 5. Plot
                im = freq_masked.plot(
                    ax=ax, 
                    cmap='Reds',   
                    vmin=0, 
                    vmax=1,        
                    add_colorbar=False
                )
            else:
                ax.text(0.5, 0.5, "No Data", ha='center')

        except Exception as e:
            print(f"Error on {model} {p_name}: {e}")
            ax.text(0.5, 0.5, "Error", ha='center')

        # Subplot Formatting
        ax.set_facecolor('whitesmoke')
        ax.set_title(f"Model: {model}", fontweight='bold')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')

    # Finalize Figure for this Period
    cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7]) 
    if 'im' in locals(): 
        cbar = fig.colorbar(im, cax=cbar_ax)
        cbar.set_label('Frequency (0 = Never, 1 = Every Year)', fontsize=12)
    
    fig.suptitle(f"Synchronized Events: {p_name.upper()} ({start_yr}-{end_yr})\n({mode.capitalize()}, {rcp_target.upper()})", fontsize=16)
    
    plt.subplots_adjust(top=0.9, bottom=0.1, left=0.1, right=0.9, hspace=0.3, wspace=0.2)
    plt.show()