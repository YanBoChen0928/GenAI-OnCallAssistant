# /scripts/compare_subsets_opt.py
import pandas as pd
from pathlib import Path
from datetime import datetime

def load_and_compare_subsets(format_type='csv'):
    """
    Load and compare the first 10 records from both optimized subsets
    
    Args:
        format_type (str): 'csv' or 'jsonl'
    """
    # Prepare output file
    output_dir = Path("../analysis")
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"subset_comparison_first10_records_{timestamp}.md"
    
    # Initialize markdown content
    md_content = []
    md_content.append("# Optimized Subsets Comparison Report\n")
    md_content.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    md_content.append(f"File format: {format_type.upper()}\n")
    
    # Set file paths based on format
    if format_type == 'csv':
        emergency_path = "../dataset/emergency/emergency_subset_opt.csv"
        treatment_path = "../dataset/emergency_treatment/emergency_treatment_subset_opt.csv"
        # Load CSV files
        emergency_df = pd.read_csv(emergency_path)
        treatment_df = pd.read_csv(treatment_path)
    else:  # jsonl
        emergency_path = "../dataset/emergency/emergency_subset_opt.jsonl"
        treatment_path = "../dataset/emergency_treatment/emergency_treatment_subset_opt.jsonl"
        # Load JSONL files
        emergency_df = pd.read_json(emergency_path, lines=True)
        treatment_df = pd.read_json(treatment_path, lines=True)
    
    # Print and save basic statistics
    print("\n📊 Basic Statistics:")
    print("-" * 40)
    md_content.append("\n## Basic Statistics\n")
    
    stats = [
        f"- Emergency subset total records: {len(emergency_df)}",
        f"- Emergency+Treatment subset total records: {len(treatment_df)}",
        f"- Avg Emergency Text Length: {emergency_df['clean_text'].str.len().mean():.2f}",
        f"- Avg Treatment Text Length: {treatment_df['clean_text'].str.len().mean():.2f}"
    ]
    
    # Calculate average keywords using pattern
    pattern = r'\|'
    emergency_avg = emergency_df['matched'].str.count(pattern).add(1).mean()
    treatment_avg = treatment_df['matched'].str.count(pattern).add(1).mean()
    
    stats.extend([
        f"- Avg Emergency Keywords: {emergency_avg:.2f}",
        f"- Avg Treatment Keywords: {treatment_avg:.2f}"
    ])
    
    # Print to console and add to markdown
    for stat in stats:
        print(stat.replace("- ", ""))
    md_content.extend(stats)
    
    # Compare first 10 records from Emergency subset
    print("\n🔍 First 10 records from Emergency Subset:")
    print("-" * 80)
    md_content.append("\n## Emergency Subset (First 10 Records)\n")
    
    for idx, row in emergency_df.head(10).iterrows():
        print(f"\nRecord #{idx+1}")
        print(f"Text preview: {row['clean_text'][:100]}...")
        print(f"Matched keywords: {row['matched']}")
        print(f"Text length: {len(row['clean_text'])}")
        print("-" * 40)
        
        md_content.extend([
            f"\n### Record {idx+1}",
            "```",
            f"Text preview: {row['clean_text'][:100]}...",
            f"Matched keywords: {row['matched']}",
            f"Text length: {len(row['clean_text'])}",
            "```\n"
        ])
    
    # Compare first 10 records from Emergency+Treatment subset
    print("\n🔍 First 10 records from Emergency+Treatment Subset:")
    print("-" * 80)
    md_content.append("\n## Emergency+Treatment Subset (First 10 Records)\n")
    
    for idx, row in treatment_df.head(10).iterrows():
        print(f"\nRecord #{idx+1}")
        print(f"Text preview: {row['clean_text'][:100]}...")
        print(f"Emergency keywords: {row['matched']}")
        print(f"Treatment keywords: {row['treatment_matched']}")
        print(f"Text length: {len(row['clean_text'])}")
        print("-" * 40)
        
        md_content.extend([
            f"\n### Record {idx+1}",
            "```",
            f"Text preview: {row['clean_text'][:100]}...",
            f"Emergency keywords: {row['matched']}",
            f"Treatment keywords: {row['treatment_matched']}",
            f"Text length: {len(row['clean_text'])}",
            "```\n"
        ])
    
    # Save markdown content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_content))
    
    print(f"\n✅ Comparison complete!")
    print(f"Report saved to: {output_file}")

if __name__ == "__main__":
    # Compare using CSV format
    print("\nComparing CSV files...")
    load_and_compare_subsets('csv')
    
    # Compare using JSONL format
    print("\nComparing JSONL files...")
    load_and_compare_subsets('jsonl')
