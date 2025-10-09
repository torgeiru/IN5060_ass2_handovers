#!/usr/bin/env python3
"""
CSV Data Processor for Network Measurements
Processes operator-specific network measurement data by:
1. Extracting operator-agnostic and operator 1 specific features
2. Filling missing values using forward fill then backward fill
3. Maintaining input folder structure in output
"""

import pandas as pd
import sys
import os
from pathlib import Path


def get_operator1_columns(df):
    """
    Extract specific column names: operator-agnostic (Day, Timestamp) 
    and operator 1 specific features.
    
    Args:
        df: Input DataFrame
        
    Returns:
        List of column names to keep
    """
    columns_to_keep = []
    
    # Operator-agnostic features to keep
    agnostic_features = ['Day', 'Timestamp [dd.mm.yyyy,hh:mm:ss.ss]']
    
    # Operator 1 specific features to keep (without the ": [1]" suffix in search)
    operator1_features = [
      '5G NR UE_Cell Environment_1. PCI',
      'QoS Tester_QP Interactivity Progress_Cur. Round-trip Latency (median)',
      'QoS Tester_QP Interactivity Result_Round-trip Latency (median)'
    ]
    
    for col in df.columns:
        # Check for operator-agnostic columns
        if col in agnostic_features:
            columns_to_keep.append(col)
        # Check for operator 1 specific columns
        else:
            for feature in operator1_features:
                if col.startswith(feature) and col.endswith(': [1]'):
                    columns_to_keep.append(col)
                    break
    
    return columns_to_keep


def fill_missing_values(df):
    """
    Fill missing values (?) using forward fill then backward fill.
    Preserves data types appropriately.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with filled values
    """
    # Replace '?' with NaN for proper handling
    df_filled = df.replace('?', pd.NA)
    
    # Apply forward fill then backward fill
    df_filled = df_filled.ffill().bfill()
    
    return df_filled


def process_csv_file(input_path, output_path):
    """
    Process a single CSV file: extract operator 1 data and fill missing values.
    
    Args:
        input_path: Path to input CSV file
        output_path: Path to output CSV file
    """
    try:
        # Read CSV with semicolon delimiter
        df = pd.read_csv(input_path, sep=';', low_memory=False)
        
        # Extract operator 1 columns
        operator1_columns = get_operator1_columns(df)
        df_operator1 = df[operator1_columns].copy()
        
        # Fill missing values
        df_processed = fill_missing_values(df_operator1)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save processed data
        df_processed.to_csv(output_path, sep=';', index=False)
        
        print(f"✓ Processed: {input_path.name}")
        
    except Exception as e:
        print(f"✗ Error processing {input_path}: {str(e)}")
        raise


def process_folder_structure(input_root, output_root):
    """
    Process all CSV files maintaining the folder structure.
    
    Args:
        input_root: Root directory containing input CSV files
        output_root: Root directory for output CSV files
    """
    input_path = Path(input_root)
    output_path = Path(output_root)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input path does not exist: {input_root}")
    
    # Find all CSV files recursively
    csv_files = list(input_path.rglob('*.csv'))
    
    if not csv_files:
        print(f"No CSV files found in {input_root}")
        return
    
    print(f"Found {len(csv_files)} CSV file(s) to process\n")
    
    # Process each CSV file
    for csv_file in csv_files:
        # Calculate relative path from input root
        relative_path = csv_file.relative_to(input_path)
        
        # Create corresponding output path
        output_file = output_path / relative_path
        
        # Process the file
        process_csv_file(csv_file, output_file)
    
    print(f"\n✓ All files processed successfully!")
    print(f"Output saved to: {output_root}")


def main():
    """Main entry point for the CSV processor."""
    if len(sys.argv) != 3:
        print("Usage: python3 ./create_dataset.py <input CSV path> <output CSV path>")
        print("\nExample:")
        print("  python3 ./create_dataset.py ./input_data ./output_data")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    print("="*60)
    print("CSV Data Processor for Network Measurements")
    print("="*60)
    print(f"Input path:  {input_path}")
    print(f"Output path: {output_path}")
    print("="*60 + "\n")
    
    try:
        process_folder_structure(input_path, output_path)
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()