# /scripts/data_explorer_treatment_opt.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import json
import numpy as np
from tqdm import tqdm
import re

def calculate_density(matches, text_length):
    """
    Calculate keyword density per 1000 words
    
    Args:
        matches: Number of keyword matches
        text_length: Total text length
        
    Returns:
        float: Density per 1000 words
    """
    return (matches / text_length) * 1000

def analyze_treatment_subset(
    treatment_file_path, 
    emergency_keywords_path, 
    treatment_keywords_path, 
    output_dir="analysis_treatment_opt"  # Updated default output directory
):
    """
    Specialized analysis for optimized treatment subset focusing on:
    1. Dual keyword analysis (emergency + treatment)
    2. Path B effectiveness validation
    3. Condition mapping data preparation
    4. RAG readiness assessment
    """
    print(f"\n{'='*60}")
    print(f"Treatment Subset Analysis (Optimized Version)")
    print(f"Treatment file: {treatment_file_path}")
    print(f"Emergency keywords: {emergency_keywords_path}")
    print(f"Treatment keywords: {treatment_keywords_path}")
    print(f"Output directory: {output_dir}")
    print(f"{'='*60}\n")
    
    # Load data
    print("1️⃣ Loading optimized treatment subset data...")
    df = pd.read_csv(treatment_file_path)
    output_dir = Path(output_dir)
    
    # Load keyword lists
    print("2️⃣ Loading keyword lists...")
    with open(emergency_keywords_path, 'r', encoding='utf-8') as f:
        emergency_keywords = [line.strip() for line in f if line.strip()]
    
    with open(treatment_keywords_path, 'r', encoding='utf-8') as f:
        treatment_keywords = [line.strip() for line in f if line.strip()]
    
    print(f"   Emergency keywords: {len(emergency_keywords)}")
    print(f"   Treatment keywords: {len(treatment_keywords)}")
    
    # Basic statistics
    print("\n3️⃣ Computing basic statistics...")
    total_records = len(df)
    df['text_length'] = df['clean_text'].str.len()
    avg_length = df['text_length'].mean()
    
    print(f"   Total treatment records: {total_records}")
    print(f"   Average text length: {avg_length:.2f} characters")
    
    # Initialize comprehensive statistics
    stats = {
        'basic_statistics': {
            'total_records': int(total_records),
            'avg_text_length': float(avg_length),
            'emergency_keywords_count': len(emergency_keywords),
            'treatment_keywords_count': len(treatment_keywords)
        },
        'emergency_keyword_stats': {},
        'treatment_keyword_stats': {},
        'cooccurrence_analysis': {},
        'path_b_validation': {},
        'condition_mapping_candidates': {}
    }
    
    # Emergency keyword analysis in treatment subset
    print("\n4️⃣ Analyzing emergency keywords in treatment subset...")
    for keyword in emergency_keywords:
        count = df['clean_text'].str.contains(keyword, case=False, na=False).sum()
        stats['emergency_keyword_stats'][keyword] = int(count)
        print(f"   Emergency: {keyword} -> {count} records")
    
    # Treatment keyword analysis
    print("\n5️⃣ Analyzing treatment keywords...")
    for keyword in treatment_keywords:
        count = df['clean_text'].str.contains(keyword, case=False, na=False).sum()
        stats['treatment_keyword_stats'][keyword] = int(count)
        print(f"   Treatment: {keyword} -> {count} records")
    
    # Step 6: Co-occurrence analysis
    print("\n6️⃣ Computing keyword co-occurrence patterns...")

    # Initialize matrices for full dataset
    emergency_matrix = np.zeros((len(df), len(emergency_keywords)), dtype=bool)
    treatment_matrix = np.zeros((len(df), len(treatment_keywords)), dtype=bool)

    # Pre-process text
    print("   Pre-processing text...")
    df['clean_text_lower'] = df['clean_text'].fillna('').str.lower()

    # Process all emergency keywords
    print("\n   Processing all emergency keywords...")
    for i, keyword in enumerate(tqdm(emergency_keywords, desc="Emergency keywords")):
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        emergency_matrix[:, i] = df['clean_text_lower'].str.contains(pattern, regex=True, na=False)
        matches = emergency_matrix[:, i].sum()
        print(f"   - {keyword}: {matches} matches")

    # Process all treatment keywords
    print("\n   Processing all treatment keywords...")
    for i, keyword in enumerate(tqdm(treatment_keywords, desc="Treatment keywords")):
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        treatment_matrix[:, i] = df['clean_text_lower'].str.contains(pattern, regex=True, na=False)
        matches = treatment_matrix[:, i].sum()
        print(f"   - {keyword}: {matches} matches")

    # Compute co-occurrence matrix
    print("\n   Computing co-occurrence matrix...")
    cooc_matrix = emergency_matrix.astype(int).T @ treatment_matrix.astype(int)
    print("   Computation completed successfully")

    # Extract results
    print("   Extracting co-occurrence pairs...")
    cooccurrence_pairs = []
    for i, em_kw in enumerate(emergency_keywords):
        for j, tr_kw in enumerate(treatment_keywords):
            count = int(cooc_matrix[i, j])
            if count > 0:
                cooccurrence_pairs.append({
                    'emergency_keyword': em_kw,
                    'treatment_keyword': tr_kw,
                    'cooccurrence_count': count,
                    'percentage': float(count / len(df) * 100)
                })

    # Sort and store results
    cooccurrence_pairs.sort(key=lambda x: x['cooccurrence_count'], reverse=True)
    stats['cooccurrence_analysis'] = cooccurrence_pairs[:20]  # Top 20 pairs

    print(f"   Found {len(cooccurrence_pairs)} co-occurrence pairs")
    print("   Top 5 co-occurrence pairs:")
    for i, pair in enumerate(cooccurrence_pairs[:5]):
        print(f"     {i+1}. {pair['emergency_keyword']} + {pair['treatment_keyword']}: {pair['cooccurrence_count']} ({pair['percentage']:.1f}%)")
    
    # Step 7: Path B validation metrics
    print("\n7️⃣ Validating Path B strategy effectiveness...")
    
    # Compute keyword density with progress bar
    print("   Computing keyword density...")
    with tqdm(total=2, desc="Density calculation") as pbar:
        emergency_density = calculate_density(
            emergency_matrix.sum(axis=1),
            df['text_length']
        )
        pbar.update(1)
        
        treatment_density = calculate_density(
            treatment_matrix.sum(axis=1),
            df['text_length']
        )
        pbar.update(1)
    
    # Store density in dataframe for visualization
    df['emergency_keyword_density'] = emergency_density
    df['treatment_keyword_density'] = treatment_density
    
    # Calculate statistics with the new density metrics
    stats['path_b_validation'] = {
        'avg_emergency_density': float(np.mean(emergency_density)),
        'avg_treatment_density': float(np.mean(treatment_density)),
        'high_density_records': int(sum(
            (emergency_density >= np.percentile(emergency_density, 75)) & 
            (treatment_density >= np.percentile(treatment_density, 75))
        )),
        'precision_estimate': float(sum(
            (emergency_density > 0) & (treatment_density > 0)
        ) / len(df))
    }
    
    # Print detailed results
    print("\n   Results:")
    print(f"   - Average emergency keyword density (per 1000 words): {stats['path_b_validation']['avg_emergency_density']:.2f}")
    print(f"   - Average treatment keyword density (per 1000 words): {stats['path_b_validation']['avg_treatment_density']:.2f}")
    print(f"   - High-density records (top 25% in both): {stats['path_b_validation']['high_density_records']}")
    print(f"   - Precision estimate: {stats['path_b_validation']['precision_estimate']:.2f}")
    
    # Sample distribution analysis
    print("\n   Density Distribution:")
    density_counts = pd.DataFrame({
        'emergency': pd.qcut(emergency_density, q=4, labels=['Low', 'Medium-Low', 'Medium-High', 'High']),
        'treatment': pd.qcut(treatment_density, q=4, labels=['Low', 'Medium-Low', 'Medium-High', 'High'])
    }).value_counts().head()
    print("   Top 5 density combinations (emergency, treatment):")
    for (em, tr), count in density_counts.items():
        print(f"   - {count} documents have {em} emergency and {tr} treatment density")
    
    # Visualization
    print("\n8️⃣ Generating visualizations...")
    output_plots = output_dir / "plots"
    output_plots.mkdir(parents=True, exist_ok=True)
    
    # 1. Keyword density scatter plot with improved visualization
    plt.figure(figsize=(12, 8))
    plt.scatter(
        emergency_density,
        treatment_density,
        alpha=0.6,
        c=np.log1p(df['text_length']),
        cmap='viridis'
    )
    plt.colorbar(label='Log Text Length')
    plt.xlabel('Emergency Keyword Density (per 1000 words)')
    plt.ylabel('Treatment Keyword Density (per 1000 words)')
    plt.title('Emergency vs Treatment Keyword Density (Optimized)')
    plt.grid(True, alpha=0.3)
    
    # Add mean lines
    plt.axvline(x=np.mean(emergency_density), color='r', linestyle='--', alpha=0.5, label='Mean Emergency Density')
    plt.axhline(y=np.mean(treatment_density), color='g', linestyle='--', alpha=0.5, label='Mean Treatment Density')
    plt.legend()
    
    plt.savefig(output_plots / "keyword_density_scatter_opt.png", bbox_inches='tight', dpi=300)
    plt.close()
    
    # Save comprehensive statistics
    print("\n9️⃣ Saving analysis results...")
    stats_dir = output_dir / "stats"
    stats_dir.mkdir(parents=True, exist_ok=True)
    
    with open(stats_dir / "treatment_analysis_comprehensive_opt.json", 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Treatment subset analysis complete! (Optimized Version)")
    print(f"   Results saved to: {output_dir}")
    print(f"   Plots: {output_plots}")
    print(f"   Statistics: {stats_dir}")
    
    return stats

if __name__ == "__main__":
    # Configuration for optimized version
    treatment_file = "../dataset/emergency_treatment/emergency_treatment_subset_opt.csv"
    emergency_keywords = "../keywords/emergency_keywords.txt"
    treatment_keywords = "../keywords/treatment_keywords.txt"
    output_directory = "../analysis_treatment_opt"
    
    # Run analysis
    results = analyze_treatment_subset(
        treatment_file, 
        emergency_keywords, 
        treatment_keywords, 
        output_directory
    ) 