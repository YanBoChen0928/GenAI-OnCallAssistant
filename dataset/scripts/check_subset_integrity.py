#!/usr/bin/env python3
# /scripts/check_subset_integrity.py

import pandas as pd
import json
from pathlib import Path
from tqdm import tqdm

def check_subset_sample(file_path, sample_size=100):
    """
    Check the first N rows of the subset file
    """
    print(f"\n{'='*60}")
    print(f"📊 Sampling Analysis (first {sample_size} rows)")
    print(f"{'='*60}")
    
    # Read sample
    print(f"\n1️⃣ Reading sample from: {file_path}")
    sample_df = pd.read_csv(file_path, nrows=sample_size)
    
    # Basic information
    print("\n2️⃣ Basic Information:")
    print(f"   Columns present: {', '.join(sample_df.columns.tolist())}")
    
    # Check matched columns
    print("\n3️⃣ Matched Columns Status:")
    matched_stats = {
        'matched': {
            'non_null': int(sample_df['matched'].notna().sum()),
            'non_empty': int((sample_df['matched'].str.len() > 0).sum()),
            'unique_values': sample_df['matched'].nunique()
        },
        'treatment_matched': {
            'non_null': int(sample_df['treatment_matched'].notna().sum()),
            'non_empty': int((sample_df['treatment_matched'].str.len() > 0).sum()),
            'unique_values': sample_df['treatment_matched'].nunique()
        }
    }
    
    for col, stats in matched_stats.items():
        print(f"\n   {col}:")
        print(f"   - Non-null count: {stats['non_null']}/{sample_size}")
        print(f"   - Non-empty count: {stats['non_empty']}/{sample_size}")
        print(f"   - Unique values: {stats['unique_values']}")
    
    # Sample rows with both matches
    print("\n4️⃣ Sample Rows with Both Matches:")
    both_matched = sample_df[
        (sample_df['matched'].notna() & sample_df['matched'].str.len() > 0) &
        (sample_df['treatment_matched'].notna() & sample_df['treatment_matched'].str.len() > 0)
    ].head(3)
    
    for idx, row in both_matched.iterrows():
        print(f"\n   Row {idx}:")
        print(f"   - Emergency keywords: {row['matched']}")
        print(f"   - Treatment keywords: {row['treatment_matched']}")
    
    return matched_stats

def analyze_large_file(file_path, chunk_size=1000):
    """
    Analyze the entire file in chunks
    """
    print(f"\n{'='*60}")
    print(f"📈 Full File Analysis (chunk size: {chunk_size})")
    print(f"{'='*60}")
    
    stats = {
        'total_rows': 0,
        'matched_stats': {
            'non_null': 0,
            'non_empty': 0
        },
        'treatment_matched_stats': {
            'non_null': 0,
            'non_empty': 0
        },
        'both_matched': 0
    }
    
    print("\n1️⃣ Processing file in chunks...")
    chunks = pd.read_csv(file_path, chunksize=chunk_size)
    
    for chunk in tqdm(chunks, desc="Analyzing chunks"):
        # Update total rows
        stats['total_rows'] += len(chunk)
        
        # Update matched stats
        stats['matched_stats']['non_null'] += chunk['matched'].notna().sum()
        stats['matched_stats']['non_empty'] += (chunk['matched'].str.len() > 0).sum()
        
        # Update treatment_matched stats
        stats['treatment_matched_stats']['non_null'] += chunk['treatment_matched'].notna().sum()
        stats['treatment_matched_stats']['non_empty'] += (chunk['treatment_matched'].str.len() > 0).sum()
        
        # Update both matched count
        stats['both_matched'] += (
            (chunk['matched'].notna() & chunk['matched'].str.len() > 0) &
            (chunk['treatment_matched'].notna() & chunk['treatment_matched'].str.len() > 0)
        ).sum()
    
    return stats

def generate_report(sample_stats, full_stats, output_dir):
    """
    Generate and save analysis report
    """
    print(f"\n{'='*60}")
    print(f"📝 Generating Report")
    print(f"{'='*60}")
    
    report = {
        'sample_analysis': sample_stats,
        'full_file_analysis': {
            'total_records': int(full_stats['total_rows']),
            'matched_column': {
                'non_null_count': int(full_stats['matched_stats']['non_null']),
                'non_empty_count': int(full_stats['matched_stats']['non_empty']),
                'null_percentage': float(
                    (full_stats['total_rows'] - full_stats['matched_stats']['non_null']) 
                    / full_stats['total_rows'] * 100
                )
            },
            'treatment_matched_column': {
                'non_null_count': int(full_stats['treatment_matched_stats']['non_null']),
                'non_empty_count': int(full_stats['treatment_matched_stats']['non_empty']),
                'null_percentage': float(
                    (full_stats['total_rows'] - full_stats['treatment_matched_stats']['non_null']) 
                    / full_stats['total_rows'] * 100
                )
            },
            'both_matched_count': int(full_stats['both_matched']),
            'both_matched_percentage': float(
                full_stats['both_matched'] / full_stats['total_rows'] * 100
            )
        }
    }
    
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save report
    report_file = output_dir / 'integrity_check_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nReport saved to: {report_file}")
    
    # Print summary
    print("\n📊 Summary:")
    print(f"Total records: {report['full_file_analysis']['total_records']}")
    print(f"Records with both matches: {report['full_file_analysis']['both_matched_count']} "
          f"({report['full_file_analysis']['both_matched_percentage']:.2f}%)")
    
    return report

def main():
    """
    Main execution function
    """
    # Configuration
    input_file = "../dataset/emergency_treatment/emergency_treatment_subset.csv"
    output_dir = "../analysis/integrity_check"
    
    print(f"\n🔍 Starting Subset Integrity Check")
    print(f"Input file: {input_file}")
    print(f"Output directory: {output_dir}")
    
    # Run analysis
    sample_stats = check_subset_sample(input_file)
    full_stats = analyze_large_file(input_file)
    report = generate_report(sample_stats, full_stats, output_dir)
    
    print("\n✅ Integrity check complete!")

if __name__ == "__main__":
    main() 