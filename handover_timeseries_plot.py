#!/usr/bin/env python3
"""
Handover Time Series Plot Generator

Usage:
    python3 ./handover_timeseries_plot.py <input_folder> <output_folder>

Example:
    python3 ./handover_timeseries_plot.py ./handover_data ./plots
"""

import sys
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def parse_csv_file(csv_path):
    """Parse CSV file and return DataFrame."""
    df = pd.read_csv(csv_path, sep=';')
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()
    return df


def extract_handovers(df):
    """Extract individual handovers from DataFrame."""
    handovers = []
    for event_id in df['handover_event_id'].unique():
        handover_df = df[df['handover_event_id'] == event_id].copy()
        handovers.append(handover_df)
    return handovers


def center_handover_at_origin(handover_df):
    """
    Center the handover at the origin based on the handover point.
    Returns new x positions and y values (interactivity scores).
    """
    # Find the handover point
    handover_point_idx = handover_df[handover_df['is_handover_point'] == True].index
    
    if len(handover_point_idx) == 0:
        # No handover point marked, use middle of window
        handover_point_row = len(handover_df) // 2
    else:
        handover_point_row = handover_df.loc[handover_point_idx[0], 'row_in_window']
    
    # Create centered x positions
    x_positions = handover_df['row_in_window'].values - handover_point_row
    
    # Get interactivity scores
    score_col = 'QoS Tester_QP Interactivity Progress_Cur. Interactivity Score [%] : [1]'
    y_values = handover_df[score_col].values
    
    # Get PCI values for coloring
    pci_col = '5G NR UE_Cell Environment_1. PCI : [1]'
    pci_values = handover_df[pci_col].values
    
    return x_positions, y_values, pci_values, handover_point_row


def plot_handovers(handovers, output_path, location_name):
    """Plot all handovers on the same figure."""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    colors = plt.cm.tab10.colors
    
    for idx, handover_df in enumerate(handovers):
        x_pos, y_vals, pci_vals, ho_point = center_handover_at_origin(handover_df)
        
        # Plot the handover with a unique color
        color = colors[idx % len(colors)]
        label = f'Handover {idx}'
        
        ax.plot(x_pos, y_vals, marker='o', markersize=4, linewidth=1.5, 
                label=label, color=color, alpha=0.7)
        
        # Mark the handover point with a larger marker
        handover_point_mask = handover_df['is_handover_point'] == True
        if handover_point_mask.any():
            ho_x = x_pos[handover_point_mask]
            ho_y = y_vals[handover_point_mask]
            ax.scatter(ho_x, ho_y, s=200, marker='*', color=color, 
                      edgecolors='black', linewidths=2, zorder=5)
    
    # Add vertical line at origin (handover point)
    ax.axvline(x=0, color='red', linestyle='--', linewidth=2, 
               label='Handover Point', alpha=0.5)
    
    ax.set_xlabel('Relative Position (samples from handover point)', fontsize=12)
    ax.set_ylabel('Interactivity Score (%)', fontsize=12)
    ax.set_title(f'Handover Time Series - {location_name}', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved plot: {output_path}")


def process_location_file(csv_path, output_folder):
    """Process a single location CSV file and generate plot."""
    # Parse CSV
    df = parse_csv_file(csv_path)
    
    # Extract handovers
    handovers = extract_handovers(df)
    
    # Generate output filename
    csv_filename = os.path.basename(csv_path)
    location_name = csv_filename.replace('.csv', '')
    output_filename = f"{location_name}.png"
    output_path = os.path.join(output_folder, output_filename)
    
    # Plot handovers
    plot_handovers(handovers, output_path, location_name)
    
    return len(handovers)


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 handover_timeseries_plot.py <input_folder> <output_folder>")
        sys.exit(1)
    
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    
    # Validate input folder
    if not os.path.exists(input_folder):
        print(f"Error: Input folder '{input_folder}' does not exist.")
        sys.exit(1)
    
    # Create output folder if it doesn't exist
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    # Find all CSV files in input folder
    csv_pattern = os.path.join(input_folder, "*.csv")
    csv_files = glob.glob(csv_pattern)
    
    if not csv_files:
        print(f"No CSV files found in '{input_folder}'")
        sys.exit(1)
    
    print(f"Found {len(csv_files)} CSV file(s) to process")
    print("-" * 60)
    
    # Process each CSV file
    total_handovers = 0
    for csv_path in sorted(csv_files):
        print(f"Processing: {os.path.basename(csv_path)}")
        num_handovers = process_location_file(csv_path, output_folder)
        total_handovers += num_handovers
        print(f"  - Found {num_handovers} handover event(s)")
    
    print("-" * 60)
    print(f"Complete! Processed {total_handovers} total handover events")
    print(f"Output saved to: {output_folder}")


if __name__ == "__main__":
    main()