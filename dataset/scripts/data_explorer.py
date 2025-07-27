# /scripts/data_explorer.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import json

def analyze_subset(file_path, keywords_path, output_dir="analysis"):
    """Analyze subset data quality and distribution"""
    print(f"\n{'='*50}")
    print(f"Starting dataset analysis: {file_path}")
    print(f"Using keywords file: {keywords_path}")
    print(f"Output directory: {output_dir}")
    print(f"{'='*50}\n")
    
    # Load data
    print("1️⃣ Loading data...")
    df = pd.read_csv(file_path)
    output_dir = Path(output_dir)
    
    # 1. Basic statistics
    print("\n2️⃣ Calculating basic statistics...")
    total = len(df)
    df['text_length'] = df['clean_text'].str.len()
    avg_len = df['text_length'].mean()
    print(f"Total records: {total}")
    print(f"Average text length: {avg_len:.2f}")
    
    # Initialize statistics dictionary with native Python types
    stats = {
        'basic_statistics': {
            'total_records': int(total),
            'avg_length': float(avg_len)
        },
        'keyword_statistics': {}
    }
    
    # 2. Keyword analysis
    print("\n3️⃣ Performing keyword analysis...")
    with open(keywords_path, 'r') as f:
        keywords = [line.strip() for line in f if line.strip()]
    print(f"Loaded {len(keywords)} keywords")
    
    # Count keywords and store in stats
    for keyword in keywords:
        cnt = df['clean_text'].str.contains(keyword, case=False).sum()
        stats['keyword_statistics'][keyword] = int(cnt)
        print(f"  - {keyword}: {cnt} records")
    
    # 3. Visualization
    print("\n4️⃣ Generating visualizations...")
    output_path = Path(output_dir) / "plots"
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"Charts will be saved in: {output_path}")
    
    # 3.1 Keyword distribution chart
    print("  - Generating keyword distribution chart...")
    plt.figure(figsize=(15, 8))
    plt.bar(stats['keyword_statistics'].keys(), stats['keyword_statistics'].values())
    plt.xticks(rotation=45, ha='right')
    # TODO: change the title to the name of the subset
    plt.title('Keyword Distribution for Emergency Subset')
    plt.xlabel('Keywords')
    plt.ylabel('Match Count')
    # TODO: change the name of the file to the name of the subset
    plt.savefig(output_path / "keyword_distribution_emergency_subset.png", bbox_inches='tight')
    plt.close()
    
    # 3.2 Text length distribution
    print("  - Generating text length distribution...")
    plt.figure(figsize=(10, 6))
    df['text_length'].hist(bins=50)
    plt.title('Text Length Distribution')
    plt.xlabel('Text Length')
    plt.ylabel('Frequency')
    # TODO: change the name of the file to the name of the subset
    plt.savefig(output_path / "text_length_dist_emergency_subset.png", bbox_inches='tight')
    plt.close()
    
    # 3.3 Keyword co-occurrence analysis
    print("  - Generating keyword co-occurrence heatmap...")
    cooccurrence_matrix = np.zeros((len(keywords), len(keywords)))
    for text in df['clean_text']:
        present_keywords = [k for k in keywords if k.lower() in text.lower()]
        for i, k1 in enumerate(present_keywords):
            for j, k2 in enumerate(present_keywords):
                if i != j:
                    cooccurrence_matrix[keywords.index(k1)][keywords.index(k2)] += 1
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(cooccurrence_matrix, 
                xticklabels=keywords, 
                yticklabels=keywords,
                cmap='YlOrRd')
    plt.title('Keyword Co-occurrence Heatmap')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    # TODO: change the name of the file to the name of the subset
    plt.savefig(output_path / "keyword_cooccurrence_emergency_subset.png", bbox_inches='tight')
    plt.close()
    
    # 4. Save statistics
    print("\n5️⃣ Saving statistics...")
    stats_path = Path(output_dir) / "stats"
    stats_path.mkdir(parents=True, exist_ok=True)
    # TODO: change the name of the file to the name of the subset
    stats_file = stats_path / "analysis_stats_emergency_subset.json"
    
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"Statistics saved to: {stats_file}")
    
    print(f"\n✅ Analysis complete! All results saved to {output_dir} directory")

if __name__ == "__main__":
    # Set file paths
    emergency_subset = "../dataset/emergency/emergency_subset.csv"
    emergency_keywords = "../keywords/emergency_keywords.txt"
    output_dir = "../analysis"
    
    # Run analysis
    analyze_subset(emergency_subset, emergency_keywords, output_dir)