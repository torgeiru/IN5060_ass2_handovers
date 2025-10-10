#!/usr/bin/env python3
"""
Handover Statistical Analysis and Letter Plot Generator

Usage:
    python3 ./handover_statistics_plot.py <input_folder> <output_folder>

Example:
    python3 ./handover_statistics_plot.py ./handover_data ./stats_plots
"""

import sys
import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
import string


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


def calculate_handover_metric(handover_df):
    """
    Calculate handover quality metric:
    (value_at_ho / argmax_before_ho) * (argmax_after_ho / value_at_ho)
    
    Returns the metric value or None if cannot be calculated.
    """
    score_col = 'QoS Tester_QP Interactivity Progress_Cur. Interactivity Score [%] : [1]'
    
    # Find the handover point
    handover_point_mask = handover_df['is_handover_point'] == True
    
    if not handover_point_mask.any():
        return None
    
    handover_idx = handover_df[handover_point_mask].index[0]
    handover_row = handover_df.loc[handover_idx, 'row_in_window']
    
    # Get values before and after handover
    before_mask = handover_df['row_in_window'] < handover_row
    after_mask = handover_df['row_in_window'] > handover_row
    
    if not before_mask.any() or not after_mask.any():
        return None
    
    # Get the value at handover point
    value_at_ho = handover_df.loc[handover_idx, score_col]
    
    # Get argmax before and after
    before_values = handover_df.loc[before_mask, score_col]
    after_values = handover_df.loc[after_mask, score_col]
    
    argmax_before_ho = before_values.max()
    argmax_after_ho = after_values.max()
    
    # Handle zero values (set to 0.01)
    if value_at_ho == 0:
        value_at_ho = 0.01
    if argmax_before_ho == 0:
        argmax_before_ho = 0.01
    if argmax_after_ho == 0:
        argmax_after_ho = 0.01
    
    # Calculate metric
    try:
        term1 = value_at_ho / argmax_before_ho
        term2 = argmax_after_ho / value_at_ho
        metric = term1 * term2
        return metric
    except:
        return None


def process_location_data(csv_path):
    """Process a location CSV and return metrics for all handovers."""
    df = parse_csv_file(csv_path)
    handovers = extract_handovers(df)
    
    metrics = []
    for handover_df in handovers:
        metric = calculate_handover_metric(handover_df)
        if metric is not None:
            metrics.append(metric)
    
    return metrics


def perform_statistical_tests(location_metrics):
    """
    Perform pairwise statistical tests between locations.
    Returns a dictionary with test results.
    """
    location_names = list(location_metrics.keys())
    n_locations = len(location_names)
    
    # Pairwise t-tests
    pairwise_results = {}
    
    for i in range(n_locations):
        for j in range(i + 1, n_locations):
            loc1 = location_names[i]
            loc2 = location_names[j]
            
            metrics1 = location_metrics[loc1]
            metrics2 = location_metrics[loc2]
            
            if len(metrics1) > 1 and len(metrics2) > 1:
                # Perform independent t-test
                t_stat, p_value = stats.ttest_ind(metrics1, metrics2)
                pairwise_results[(loc1, loc2)] = {
                    't_statistic': t_stat,
                    'p_value': p_value,
                    'significant': p_value < 0.05
                }
    
    return pairwise_results


def assign_letter_groups(location_metrics, pairwise_results):
    """
    Assign letter groups based on statistical significance.
    Locations that are not significantly different share letters.
    """
    location_names = sorted(location_metrics.keys())
    
    # Calculate mean for each location
    location_means = {loc: np.mean(metrics) for loc, metrics in location_metrics.items()}
    
    # Sort locations by mean (descending)
    sorted_locations = sorted(location_names, key=lambda x: location_means[x], reverse=True)
    
    # Initialize letter assignments
    letter_assignments = {loc: set() for loc in location_names}
    current_letter_idx = 0
    
    # Simple letter assignment algorithm
    for i, loc in enumerate(sorted_locations):
        if not letter_assignments[loc]:
            # Assign new letter to this location
            letter_assignments[loc].add(string.ascii_uppercase[current_letter_idx])
            
            # Check which other locations are not significantly different
            for j in range(i + 1, len(sorted_locations)):
                other_loc = sorted_locations[j]
                
                # Check if they're significantly different
                pair_key = tuple(sorted([loc, other_loc]))
                if pair_key in pairwise_results:
                    if not pairwise_results[pair_key]['significant']:
                        # Not significantly different - share the letter
                        letter_assignments[other_loc].add(string.ascii_uppercase[current_letter_idx])
            
            current_letter_idx += 1
    
    # Convert sets to sorted strings
    letter_strings = {loc: ''.join(sorted(letters)) for loc, letters in letter_assignments.items()}
    
    return letter_strings


def create_letter_plot(location_metrics, letter_assignments, output_path):
    """Create a letter plot showing means, error bars, and letter groupings."""
    location_names = sorted(location_metrics.keys())
    
    # Calculate statistics
    means = []
    std_errors = []
    letters = []
    
    for loc in location_names:
        metrics = location_metrics[loc]
        means.append(np.mean(metrics))
        std_errors.append(stats.sem(metrics))
        letters.append(letter_assignments[loc])
    
    # Create plot
    fig, ax = plt.subplots(figsize=(10, 8))
    
    x_pos = np.arange(len(location_names))
    colors = plt.cm.Set3(np.linspace(0, 1, len(location_names)))
    
    bars = ax.bar(x_pos, means, yerr=std_errors, capsize=10, 
                   color=colors, edgecolor='black', linewidth=1.5, alpha=0.8)
    
    # Add letter labels above bars
    for i, (bar, letter) in enumerate(zip(bars, letters)):
        height = bar.get_height() + std_errors[i]
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.05 * max(means),
                letter, ha='center', va='bottom', fontsize=16, fontweight='bold')
    
    # Add mean values on bars
    for i, (bar, mean) in enumerate(zip(bars, means)):
        ax.text(bar.get_x() + bar.get_width()/2., mean/2,
                f'{mean:.3f}', ha='center', va='center', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Location', fontsize=14, fontweight='bold')
    ax.set_ylabel('Handover Quality Metric', fontsize=14, fontweight='bold')
    ax.set_title('Handover Performance Comparison by Location\n(Letter groups indicate statistical similarity)', 
                 fontsize=16, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(location_names, fontsize=12)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved letter plot: {output_path}")


def create_box_plot(location_metrics, output_path):
    """Create a box plot showing distribution of metrics per location."""
    location_names = sorted(location_metrics.keys())
    data = [location_metrics[loc] for loc in location_names]
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    bp = ax.boxplot(data, labels=location_names, patch_artist=True,
                     showmeans=True, meanline=True)
    
    # Color the boxes
    colors = plt.cm.Set3(np.linspace(0, 1, len(location_names)))
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.8)
    
    ax.set_xlabel('Location', fontsize=14, fontweight='bold')
    ax.set_ylabel('Handover Quality Metric', fontsize=14, fontweight='bold')
    ax.set_title('Distribution of Handover Quality Metrics by Location', 
                 fontsize=16, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved box plot: {output_path}")


def print_statistical_summary(location_metrics, pairwise_results, letter_assignments):
    """Print statistical summary to console."""
    print("\n" + "=" * 70)
    print("STATISTICAL SUMMARY")
    print("=" * 70)
    
    # Summary statistics per location
    print("\nLocation Statistics:")
    print("-" * 70)
    for loc in sorted(location_metrics.keys()):
        metrics = location_metrics[loc]
        print(f"{loc}:")
        print(f"  N = {len(metrics)}")
        print(f"  Mean = {np.mean(metrics):.4f}")
        print(f"  Std Dev = {np.std(metrics, ddof=1):.4f}")
        print(f"  Std Error = {stats.sem(metrics):.4f}")
        print(f"  Letter Group: {letter_assignments[loc]}")
        print()
    
    # Pairwise comparisons
    print("\nPairwise Comparisons (t-tests):")
    print("-" * 70)
    for (loc1, loc2), result in sorted(pairwise_results.items()):
        sig_marker = "***" if result['significant'] else "ns"
        print(f"{loc1} vs {loc2}:")
        print(f"  t-statistic = {result['t_statistic']:.4f}")
        print(f"  p-value = {result['p_value']:.4f} {sig_marker}")
        print()
    
    print("*** = Significant at α=0.05 level")
    print("ns = Not significant")
    print("=" * 70 + "\n")


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 handover_statistics_plot.py <input_folder> <output_folder>")
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
    print("-" * 70)
    
    # Process each location
    location_metrics = {}
    
    for csv_path in sorted(csv_files):
        location_name = os.path.basename(csv_path).replace('.csv', '')
        print(f"Processing: {location_name}")
        
        metrics = process_location_data(csv_path)
        location_metrics[location_name] = metrics
        
        print(f"  - Calculated {len(metrics)} handover metrics")
    
    print("-" * 70)
    
    # Perform statistical tests
    print("\nPerforming statistical analysis...")
    pairwise_results = perform_statistical_tests(location_metrics)
    
    # Assign letter groups
    letter_assignments = assign_letter_groups(location_metrics, pairwise_results)
    
    # Create plots
    letter_plot_path = os.path.join(output_folder, "letter_plot_comparison.png")
    create_letter_plot(location_metrics, letter_assignments, letter_plot_path)
    
    box_plot_path = os.path.join(output_folder, "box_plot_comparison.png")
    create_box_plot(location_metrics, box_plot_path)
    
    # Print summary
    print_statistical_summary(location_metrics, pairwise_results, letter_assignments)
    
    # Save statistical results to text file
    stats_file = os.path.join(output_folder, "statistical_results.txt")
    with open(stats_file, 'w') as f:
        f.write("HANDOVER QUALITY STATISTICAL ANALYSIS\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("Location Statistics:\n")
        f.write("-" * 70 + "\n")
        for loc in sorted(location_metrics.keys()):
            metrics = location_metrics[loc]
            f.write(f"{loc}:\n")
            f.write(f"  N = {len(metrics)}\n")
            f.write(f"  Mean = {np.mean(metrics):.4f}\n")
            f.write(f"  Std Dev = {np.std(metrics, ddof=1):.4f}\n")
            f.write(f"  Std Error = {stats.sem(metrics):.4f}\n")
            f.write(f"  Letter Group: {letter_assignments[loc]}\n\n")
        
        f.write("\nPairwise Comparisons (t-tests):\n")
        f.write("-" * 70 + "\n")
        for (loc1, loc2), result in sorted(pairwise_results.items()):
            sig_marker = "***" if result['significant'] else "ns"
            f.write(f"{loc1} vs {loc2}:\n")
            f.write(f"  t-statistic = {result['t_statistic']:.4f}\n")
            f.write(f"  p-value = {result['p_value']:.4f} {sig_marker}\n\n")
        
        f.write("*** = Significant at α=0.05 level\n")
        f.write("ns = Not significant\n")
    
    print(f"Statistical results saved to: {stats_file}")
    print(f"\nComplete! All outputs saved to: {output_folder}")


if __name__ == "__main__":
    main()