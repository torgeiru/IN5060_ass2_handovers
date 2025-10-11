#!/usr/bin/env python3
"""
Handover Population Extractor

Extracts handover quality metrics for each location and saves populations
in multiple formats (CSV, JSON, NumPy).

Usage:
    python3 ./handover_population_extractor.py <input_folder> <output_folder>

Example:
    python3 ./handover_population_extractor.py ./handover_data ./populations
"""

import sys
import os
import glob
import pandas as pd
import numpy as np
import json
from pathlib import Path


def parse_csv_file(csv_path):
    """Parse CSV file and return DataFrame."""
    df = pd.read_csv(csv_path, sep=';')
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()
    return df


def find_score_column(df):
    """Find the interactivity score column name."""
    # Try exact match first
    for col in df.columns:
        if 'Interactivity Score' in col:
            return col
    # Fallback to any column with "Score" in it
    for col in df.columns:
        if 'Score' in col:
            return col
    return None


def extract_handovers(df):
    """Extract individual handovers from DataFrame."""
    handovers = []
    for event_id in df['handover_event_id'].unique():
        handover_df = df[df['handover_event_id'] == event_id].copy()
        handovers.append(handover_df)
    return handovers


def calculate_handover_metric(handover_df, score_col):
    """
    Calculate handover quality metric:
    (value_at_ho / argmax_before_ho) * (argmax_after_ho / value_at_ho)
    
    Returns a dictionary with metric and supporting data, or None if cannot be calculated.
    """
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
    
    # Store original values
    original_value_at_ho = value_at_ho
    original_argmax_before = argmax_before_ho
    original_argmax_after = argmax_after_ho
    
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
        
        # Convert numpy/pandas types to native Python types for JSON serialization
        return {
            'metric': float(metric),
            'value_at_handover': float(original_value_at_ho),
            'max_before_handover': float(original_argmax_before),
            'max_after_handover': float(original_argmax_after),
            'term1': float(term1),
            'term2': float(term2),
            'handover_event_id': int(handover_df['handover_event_id'].iloc[0]),
            'window_size': int(len(handover_df))
        }
    except Exception as e:
        return None


def process_location_file(csv_path):
    """
    Process a location CSV file and extract all handover metrics.
    Returns a list of metric dictionaries.
    """
    df = parse_csv_file(csv_path)
    
    # Find score column
    score_col = find_score_column(df)
    if score_col is None:
        print(f"  Error: Could not find score column")
        return []
    
    print(f"  Using score column: '{score_col}'")
    
    # Extract handovers
    handovers = extract_handovers(df)
    print(f"  Found {len(handovers)} handover events")
    
    # Calculate metrics for each handover
    population_data = []
    for handover_df in handovers:
        result = calculate_handover_metric(handover_df, score_col)
        if result is not None:
            population_data.append(result)
    
    print(f"  Calculated {len(population_data)} valid metrics")
    
    return population_data


def save_population_csv(population_data, output_path, location_name):
    """Save population data as CSV."""
    if not population_data:
        print(f"  Warning: No data to save for {location_name}")
        return
    
    df = pd.DataFrame(population_data)
    df.insert(0, 'location', location_name)
    df.to_csv(output_path, index=False)
    print(f"  Saved CSV: {output_path}")


def save_population_json(population_data, output_path, location_name):
    """Save population data as JSON."""
    if not population_data:
        print(f"  Warning: No data to save for {location_name}")
        return
    
    output = {
        'location': location_name,
        'n_samples': len(population_data),
        'population': population_data
    }
    
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"  Saved JSON: {output_path}")


def save_population_numpy(population_data, output_path, location_name):
    """Save population data as NumPy binary file."""
    if not population_data:
        print(f"  Warning: No data to save for {location_name}")
        return
    
    # Extract just the metric values
    metrics = np.array([d['metric'] for d in population_data])
    
    # Save as .npy file
    np.save(output_path, metrics)
    print(f"  Saved NumPy: {output_path}")


def save_summary_statistics(all_location_data, output_folder):
    """Save summary statistics across all locations."""
    summary_path = os.path.join(output_folder, "summary_statistics.txt")
    
    with open(summary_path, 'w') as f:
        f.write("HANDOVER POPULATION SUMMARY\n")
        f.write("=" * 80 + "\n\n")
        
        for location_name, population_data in sorted(all_location_data.items()):
            if not population_data:
                continue
            
            metrics = [d['metric'] for d in population_data]
            
            f.write(f"Location: {location_name}\n")
            f.write("-" * 80 + "\n")
            f.write(f"  Sample Size (N):        {len(metrics)}\n")
            f.write(f"  Mean:                   {np.mean(metrics):.6f}\n")
            f.write(f"  Median:                 {np.median(metrics):.6f}\n")
            f.write(f"  Std Deviation:          {np.std(metrics, ddof=1):.6f}\n")
            f.write(f"  Min:                    {np.min(metrics):.6f}\n")
            f.write(f"  Max:                    {np.max(metrics):.6f}\n")
            f.write(f"  25th Percentile:        {np.percentile(metrics, 25):.6f}\n")
            f.write(f"  75th Percentile:        {np.percentile(metrics, 75):.6f}\n")
            f.write("\n")
    
    print(f"\nSaved summary statistics: {summary_path}")


def save_combined_population(all_location_data, output_folder):
    """Save all location populations in a single combined file."""
    # CSV format
    combined_csv_path = os.path.join(output_folder, "all_locations_combined.csv")
    all_rows = []
    
    for location_name, population_data in all_location_data.items():
        for item in population_data:
            row = item.copy()
            row['location'] = location_name
            all_rows.append(row)
    
    if all_rows:
        df = pd.DataFrame(all_rows)
        # Reorder columns to put location first
        cols = ['location'] + [col for col in df.columns if col != 'location']
        df = df[cols]
        df.to_csv(combined_csv_path, index=False)
        print(f"Saved combined CSV: {combined_csv_path}")
    
    # JSON format
    combined_json_path = os.path.join(output_folder, "all_locations_combined.json")
    combined_json = {
        'total_locations': len(all_location_data),
        'total_samples': sum(len(pop) for pop in all_location_data.values()),
        'locations': {}
    }
    
    for location_name, population_data in all_location_data.items():
        combined_json['locations'][location_name] = {
            'n_samples': len(population_data),
            'population': population_data
        }
    
    with open(combined_json_path, 'w') as f:
        json.dump(combined_json, f, indent=2)
    
    print(f"Saved combined JSON: {combined_json_path}")


def print_population_summary(all_location_data):
    """Print summary to console."""
    print("\n" + "=" * 80)
    print("POPULATION EXTRACTION SUMMARY")
    print("=" * 80 + "\n")
    
    for location_name, population_data in sorted(all_location_data.items()):
        if not population_data:
            print(f"{location_name}: No valid metrics")
            continue
        
        metrics = [d['metric'] for d in population_data]
        
        print(f"{location_name}:")
        print(f"  N = {len(metrics)}")
        print(f"  Mean = {np.mean(metrics):.6f}")
        print(f"  Std = {np.std(metrics, ddof=1):.6f}")
        print(f"  Range = [{np.min(metrics):.6f}, {np.max(metrics):.6f}]")
        print()
    
    total_samples = sum(len(pop) for pop in all_location_data.values())
    print(f"Total samples across all locations: {total_samples}")
    print("=" * 80 + "\n")


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 handover_population_extractor.py <input_folder> <output_folder>")
        sys.exit(1)
    
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    
    # Validate input folder
    if not os.path.exists(input_folder):
        print(f"Error: Input folder '{input_folder}' does not exist.")
        sys.exit(1)
    
    # Create output folder structure
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    csv_folder = os.path.join(output_folder, "csv")
    json_folder = os.path.join(output_folder, "json")
    numpy_folder = os.path.join(output_folder, "numpy")
    
    Path(csv_folder).mkdir(parents=True, exist_ok=True)
    Path(json_folder).mkdir(parents=True, exist_ok=True)
    Path(numpy_folder).mkdir(parents=True, exist_ok=True)
    
    # Find all CSV files in input folder
    csv_pattern = os.path.join(input_folder, "*.csv")
    csv_files = glob.glob(csv_pattern)
    
    if not csv_files:
        print(f"No CSV files found in '{input_folder}'")
        sys.exit(1)
    
    print(f"Found {len(csv_files)} CSV file(s) to process")
    print("=" * 80 + "\n")
    
    # Process each location
    all_location_data = {}
    
    for csv_path in sorted(csv_files):
        location_name = os.path.basename(csv_path).replace('.csv', '')
        print(f"Processing: {location_name}")
        
        # Extract population data
        population_data = process_location_file(csv_path)
        all_location_data[location_name] = population_data
        
        if population_data:
            # Save in multiple formats
            csv_output = os.path.join(csv_folder, f"{location_name}_population.csv")
            save_population_csv(population_data, csv_output, location_name)
            
            json_output = os.path.join(json_folder, f"{location_name}_population.json")
            save_population_json(population_data, json_output, location_name)
            
            numpy_output = os.path.join(numpy_folder, f"{location_name}_population.npy")
            save_population_numpy(population_data, numpy_output, location_name)
        
        print()
    
    print("=" * 80)
    
    # Save combined data
    print("\nGenerating combined outputs...")
    save_combined_population(all_location_data, output_folder)
    
    # Save summary statistics
    save_summary_statistics(all_location_data, output_folder)
    
    # Print summary
    print_population_summary(all_location_data)
    
    print(f"All outputs saved to: {output_folder}/")
    print(f"  - Individual populations: csv/, json/, numpy/")
    print(f"  - Combined data: all_locations_combined.csv/json")
    print(f"  - Summary: summary_statistics.txt")


if __name__ == "__main__":
    main()