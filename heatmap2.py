#!/usr/bin/env python3
"""
Generate a 2D heatmap from handover data showing QoS Interactivity Score
before (x-axis) vs after (y-axis) handover points.
"""

import sys
import glob
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde


def process_handover_file(csv_path):
    """
    Process a single CSV file and extract before/after QoS scores for each handover.
    
    Returns:
        List of tuples (mean_before, mean_after, location) for each handover event
    """
    # Extract location from filename (e.g., location_4_aggregated.csv -> 4)
    filename = os.path.basename(csv_path)
    location = int(filename.split('_')[1])
    # Read CSV with semicolon delimiter
    df = pd.read_csv(csv_path, sep=';')
    
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()
    
    # Target column for analysis
    qos_column = 'QoS Tester_QP Interactivity Progress_Cur. Interactivity Score [%] : [1]'
    
    handover_points = []
    
    # Group by handover_event_id
    for event_id, group in df.groupby('handover_event_id'):
        # Find the handover point
        handover_idx = group[group['is_handover_point'] == True].index
        
        if len(handover_idx) == 0:
            continue
            
        handover_idx = handover_idx[0]
        
        # Get all rows for this handover event
        event_rows = group.sort_values('row_in_window')
        
        # Find position of handover point in the event
        handover_position = event_rows[event_rows.index == handover_idx]['row_in_window'].values[0]
        
        # Get 10 samples before handover (not including handover point)
        before_samples = event_rows[
            (event_rows['row_in_window'] < handover_position) &
            (event_rows['row_in_window'] >= handover_position - 10)
        ][qos_column]
        
        # Get 10 samples after handover (not including handover point)
        after_samples = event_rows[
            (event_rows['row_in_window'] > handover_position) &
            (event_rows['row_in_window'] <= handover_position + 10)
        ][qos_column]
        
        # Calculate means if we have enough samples
        if len(before_samples) > 0 and len(after_samples) > 0:
            mean_before = before_samples.mean()
            mean_after = after_samples.mean()
            handover_points.append((mean_before, mean_after, location))
    
    return handover_points


def create_heatmap(all_points, output_path):
    """
    Create a continuous 2D heatmap from scatter points using KDE.
    
    Args:
        all_points: List of (x, y, location) tuples
        output_path: Path to save the heatmap PNG
    """
    if len(all_points) == 0:
        print("No valid handover points found!")
        return
    
    # Separate x, y coordinates and locations
    x = np.array([p[0] for p in all_points])
    y = np.array([p[1] for p in all_points])
    locations = np.array([p[2] for p in all_points])
    
    # Define colors for each location
    location_colors = {
        4: '#e74c3c',  # Red
        7: '#3498db',  # Blue
        9: '#2ecc71'   # Green
    }
    
    print(f"Total handover events processed: {len(all_points)}")
    print(f"Mean QoS before: {x.mean():.2f}%")
    print(f"Mean QoS after: {y.mean():.2f}%")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # If we have enough points, create KDE heatmap
    if len(all_points) >= 2:
        # Create grid for KDE
        x_min, x_max = max(0, x.min() - 5), min(100, x.max() + 5)
        y_min, y_max = max(0, y.min() - 5), min(100, y.max() + 5)
        
        grid_size = 100
        xi = np.linspace(x_min, x_max, grid_size)
        yi = np.linspace(y_min, y_max, grid_size)
        Xi, Yi = np.meshgrid(xi, yi)
        
        # Perform KDE
        positions = np.vstack([Xi.ravel(), Yi.ravel()])
        values = np.vstack([x, y])
        
        try:
            kernel = gaussian_kde(values)
            Zi = np.reshape(kernel(positions).T, Xi.shape)
            
            # Create heatmap
            im = ax.contourf(Xi, Yi, Zi, levels=20, cmap='YlOrRd', alpha=0.8)
            plt.colorbar(im, ax=ax, label='Density')
        except:
            print("KDE failed, using scatter plot only")
    
    # Overlay scatter points with colors by location
    for loc in np.unique(locations):
        mask = locations == loc
        color = location_colors.get(loc, '#888888')
        ax.scatter(x[mask], y[mask], c=color, s=50, alpha=0.7, 
                  edgecolors='white', linewidths=1, zorder=5,
                  label=f'Location {loc}')
    
    # Add diagonal reference line (perfect correlation)
    lim_min = max(0, min(x.min(), y.min()) - 5)
    lim_max = min(100, max(x.max(), y.max()) + 5)
    ax.plot([lim_min, lim_max], [lim_min, lim_max], 
            'k--', alpha=0.3, linewidth=1, label='y=x reference')
    
    # Labels and title
    ax.set_xlabel('Mean QoS Score Before Handover [%]', fontsize=12, fontweight='bold')
    ax.set_ylabel('Mean QoS Score After Handover [%]', fontsize=12, fontweight='bold')
    ax.set_title('QoS Interactivity Score: Before vs After Handover\n(10 samples before/after)', 
                 fontsize=14, fontweight='bold')
    
    # Set limits
    ax.set_xlim(lim_min, lim_max)
    ax.set_ylim(lim_min, lim_max)
    
    # Grid
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add legend for locations
    ax.legend(loc='best', framealpha=0.9)
    
    # Save figure
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nHeatmap saved to: {output_path}")
    plt.close()


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 ./handover_timeseries_plot.py <input handover data folder> <output timeseries plots folder>")
        sys.exit(1)
    
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Glob all CSV files in input folder
    csv_pattern = os.path.join(input_folder, "*.csv")
    csv_files = glob.glob(csv_pattern)
    
    if not csv_files:
        print(f"No CSV files found in {input_folder}")
        sys.exit(1)
    
    print(f"Found {len(csv_files)} CSV file(s)")
    
    # Process all CSV files
    all_handover_points = []
    
    for csv_file in csv_files:
        print(f"\nProcessing: {os.path.basename(csv_file)}")
        try:
            points = process_handover_file(csv_file)
            all_handover_points.extend(points)
            print(f"  Extracted {len(points)} handover events")
        except Exception as e:
            print(f"  Error processing file: {e}")
            continue
    
    # Generate heatmap
    output_path = os.path.join(output_folder, "heatmap.png")
    create_heatmap(all_handover_points, output_path)


if __name__ == "__main__":
    main()