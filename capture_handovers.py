#!/usr/bin/env python3
"""
5G NR PCI Handover Aggregation and Window Extraction

This program:
1. Detects PCI handovers (changes in PCI value) for each location
2. Extracts time windows around each handover with dynamic sizing
3. Aggregates handovers across all files within each location subfolder
4. Saves windowed data and metadata for analysis

Usage: python3 capture_handovers.py <input_processed_csv_path> <output_csv_path> [--window_size SIZE]
"""

import sys
import os
import argparse
import json
from pathlib import Path
import pandas as pd
import numpy as np


def find_pci_column(df):
    """
    Find the PCI (Physical Cell ID) column in the dataframe.
    
    Returns:
        Column name or None if not found
    """
    for col in df.columns:
        if 'PCI' in col.upper() and '5G NR' in col.upper():
            return col
    
    # Fallback: any column with PCI
    for col in df.columns:
        if 'PCI' in col.upper():
            return col
    
    return None


def detect_handovers(df, pci_column):
    """
    Detect PCI handovers (changes in PCI value).
    Only detects real PCI changes, properly handles NaN values.
    
    Args:
        df: DataFrame with PCI data
        pci_column: Name of the PCI column
        
    Returns:
        List of handover indices where PCI changed
    """
    if pci_column not in df.columns:
        return []
    
    pci_series = df[pci_column].copy()
    pci_prev = pci_series.shift(1)
    
    # Detect changes: both values must be valid AND different
    handover_mask = (
        pci_series.notna() &           # Current value exists
        pci_prev.notna() &              # Previous value exists
        (pci_series != pci_prev)        # Values are different
    )
    
    handover_indices = df.index[handover_mask].tolist()
    
    # Validate: ensure actual numeric change
    validated_handovers = []
    for idx in handover_indices:
        if idx > 0:
            pci_before = df.loc[idx - 1, pci_column]
            pci_after = df.loc[idx, pci_column]
            
            if pd.notna(pci_before) and pd.notna(pci_after):
                try:
                    if float(pci_before) != float(pci_after):
                        validated_handovers.append(idx)
                except (ValueError, TypeError):
                    pass
    
    return validated_handovers


def extract_dynamic_window(df, handover_idx, window_size, pci_column):
    """
    Extract a time window around a handover point with dynamic sizing.
    
    The window is centered on the handover when possible, but adapts
    to file boundaries (can be smaller than requested).
    
    Args:
        df: Full DataFrame
        handover_idx: Index of the handover point
        window_size: Requested window size (total samples)
        pci_column: Name of the PCI column
        
    Returns:
        Dictionary with window data and metadata
    """
    total_rows = len(df)
    half_window = window_size // 2
    
    # Calculate ideal window boundaries
    ideal_start = handover_idx - half_window
    ideal_end = handover_idx + half_window
    
    # Adjust to file boundaries (dynamic sizing)
    actual_start = max(0, ideal_start)
    actual_end = min(total_rows, ideal_end)
    
    # Extract window
    window_df = df.iloc[actual_start:actual_end].copy()
    
    # Calculate handover position within the window
    handover_offset = handover_idx - actual_start
    
    # Get PCI values before and after handover
    pci_before = df.loc[handover_idx - 1, pci_column] if handover_idx > 0 else None
    pci_after = df.loc[handover_idx, pci_column]
    
    # Convert to Python types for JSON serialization
    if pd.notna(pci_before):
        pci_before = int(pci_before) if isinstance(pci_before, (int, np.integer)) else float(pci_before)
    else:
        pci_before = None
        
    if pd.notna(pci_after):
        pci_after = int(pci_after) if isinstance(pci_after, (int, np.integer)) else float(pci_after)
    else:
        pci_after = None
    
    # Calculate timestamps if available
    timestamp_col = None
    for col in df.columns:
        if 'timestamp' in col.lower():
            timestamp_col = col
            break
    
    handover_timestamp = None
    if timestamp_col and timestamp_col in df.columns:
        handover_timestamp = str(df.loc[handover_idx, timestamp_col])
    
    return {
        'window_data': window_df,
        'handover_index': int(handover_idx),
        'handover_offset': int(handover_offset),
        'requested_window_size': int(window_size),
        'actual_window_size': len(window_df),
        'window_start_idx': int(actual_start),
        'window_end_idx': int(actual_end),
        'pci_before': pci_before,
        'pci_after': pci_after,
        'handover_timestamp': handover_timestamp,
        'is_boundary_constrained': (actual_start != ideal_start or actual_end != ideal_end)
    }


def process_location_files(location_path, window_size):
    """
    Process all CSV files in a location folder and aggregate handovers.
    
    Args:
        location_path: Path to location folder
        window_size: Requested window size for extraction
        
    Returns:
        List of handover events with their windows and metadata
    """
    csv_files = sorted(location_path.glob('*.csv'))
    all_handovers = []
    
    print(f"  Processing {len(csv_files)} file(s)...")
    
    for csv_file in csv_files:
        try:
            # Read CSV (try semicolon first, then comma)
            try:
                df = pd.read_csv(csv_file, sep=';', low_memory=False)
            except:
                df = pd.read_csv(csv_file, low_memory=False)
            
            # Find PCI column
            pci_column = find_pci_column(df)
            
            if pci_column is None:
                print(f"    ⚠ No PCI column found in {csv_file.name}, skipping...")
                continue
            
            # Detect handovers
            handover_indices = detect_handovers(df, pci_column)
            
            print(f"    {csv_file.name}: {len(handover_indices)} handover(s)")
            
            # Extract windows for each handover
            for ho_idx in handover_indices:
                window_info = extract_dynamic_window(df, ho_idx, window_size, pci_column)
                
                # Add source file metadata
                window_info['source_file'] = csv_file.name
                window_info['pci_column'] = pci_column
                
                all_handovers.append(window_info)
                
        except Exception as e:
            print(f"    ✗ Error processing {csv_file.name}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    return all_handovers


def save_aggregated_handovers(handovers, output_base_path, location_name):
    """
    Save aggregated handover data in both CSV and JSON formats.
    
    Creates:
    1. CSV file: All windowed data concatenated with event IDs
    2. JSON file: Metadata for each handover event
    
    Args:
        handovers: List of handover dictionaries
        output_base_path: Base path for output files
        location_name: Name of the location
    """
    if not handovers:
        print(f"  No handovers to save for {location_name}")
        return
    
    # Prepare metadata
    metadata = {
        'location': location_name,
        'total_handovers': len(handovers),
        'window_size_requested': handovers[0]['requested_window_size'],
        'handover_events': []
    }
    
    # Prepare concatenated window data
    all_window_data = []
    
    for event_id, ho in enumerate(handovers):
        # Add identifiers to window data
        window_df = ho['window_data'].copy()
        window_df.insert(0, 'handover_event_id', event_id)
        window_df.insert(1, 'row_in_window', range(len(window_df)))
        window_df.insert(2, 'is_handover_point', 
                        [i == ho['handover_offset'] for i in range(len(window_df))])
        
        all_window_data.append(window_df)
        
        # Build metadata for this event
        event_meta = {
            'event_id': event_id,
            'source_file': ho['source_file'],
            'handover_index_in_file': ho['handover_index'],
            'handover_offset_in_window': ho['handover_offset'],
            'window_size_requested': ho['requested_window_size'],
            'window_size_actual': ho['actual_window_size'],
            'window_start_idx': ho['window_start_idx'],
            'window_end_idx': ho['window_end_idx'],
            'is_boundary_constrained': ho['is_boundary_constrained'],
            'pci_before': ho['pci_before'],
            'pci_after': ho['pci_after'],
            'pci_column': ho['pci_column']
        }
        
        if ho['handover_timestamp']:
            event_meta['handover_timestamp'] = ho['handover_timestamp']
        
        metadata['handover_events'].append(event_meta)
    
    # Concatenate all windows
    combined_df = pd.concat(all_window_data, ignore_index=True)
    
    # Save CSV with semicolon delimiter
    csv_output = output_base_path.with_suffix('.csv')
    combined_df.to_csv(csv_output, sep=';', index=False)
    print(f"  ✓ Saved window data: {csv_output.name}")
    print(f"    Total rows: {len(combined_df)}, Events: {len(handovers)}")
    
    # Save metadata as JSON
    json_output = output_base_path.with_suffix('.json')
    with open(json_output, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"  ✓ Saved metadata: {json_output.name}")


def process_all_locations(input_root, output_root, window_size):
    """
    Process all location folders and aggregate handovers.
    
    Args:
        input_root: Root directory with location subfolders
        output_root: Root directory for output
        window_size: Window size for extraction
    """
    input_path = Path(input_root)
    output_path = Path(output_root)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input path does not exist: {input_root}")
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all location subfolders (case-insensitive)
    location_folders = [d for d in input_path.iterdir() 
                       if d.is_dir() and 'location' in d.name.lower()]
    
    if not location_folders:
        raise ValueError(f"No location folders found in {input_root}")
    
    print(f"\n{'='*70}")
    print(f"5G NR PCI Handover Aggregation")
    print(f"{'='*70}")
    print(f"Input:  {input_root}")
    print(f"Output: {output_root}")
    print(f"Window size: {window_size}")
    print(f"Found {len(location_folders)} location folder(s)")
    print(f"{'='*70}\n")
    
    total_handovers = 0
    
    for location_folder in sorted(location_folders):
        location_name = location_folder.name
        print(f"Processing: {location_name}")
        
        # Process all CSV files in this location
        handovers = process_location_files(location_folder, window_size)
        total_handovers += len(handovers)
        
        # Save aggregated results
        output_file = output_path / f"{location_name}_aggregated"
        save_aggregated_handovers(handovers, output_file, location_name)
        print()
    
    print(f"{'='*70}")
    print(f"Processing Complete!")
    print(f"{'='*70}")
    print(f"Total locations: {len(location_folders)}")
    print(f"Total handovers: {total_handovers}")
    print(f"Average per location: {total_handovers / len(location_folders):.1f}")
    print(f"{'='*70}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Aggregate 5G NR PCI handovers with dynamic windowing.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default window size (100)
  python3 capture_handovers.py ./processed_data ./handover_data
  
  # Custom window size
  python3 capture_handovers.py ./processed_data ./handover_data --window_size 200
  
  # Larger window for more context
  python3 capture_handovers.py ./processed_data ./handover_data --window_size 500
        """
    )
    
    parser.add_argument('input_path', 
                       help='Input path with location subfolders containing processed CSV files')
    parser.add_argument('output_path',
                       help='Output path for aggregated handover data')
    parser.add_argument('--window_size', type=int, default=100,
                       help='Window size around handover (default: 100)')
    
    args = parser.parse_args()
    
    try:
        process_all_locations(args.input_path, args.output_path, args.window_size)
    except Exception as e:
        print(f"\n✗ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()