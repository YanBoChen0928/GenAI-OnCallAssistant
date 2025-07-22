# /scripts/data_explorer_treatment.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import json
import numpy as np
from tqdm import tqdm
import re

def analyze_treatment_subset(
    treatment_file_path, 
    emergency_keywords_path, 
    treatment_keywords_path, 
    output_dir="analysis_treatment"
):
    """
    Specialized analysis for treatment subset focusing on:
    1. Dual keyword analysis (emergency + treatment)
    2. Path B effectiveness validation
    3. Condition mapping data preparation
    4. RAG readiness assessment
    """
    print(f"\n{'='*60}")
    print(f"Treatment Subset Analysis")
    print(f"Treatment file: {treatment_file_path}")
    print(f"Emergency keywords: {emergency_keywords_path}")
    print(f"Treatment keywords: {treatment_keywords_path}")
    print(f"Output directory: {output_dir}")
    print(f"{'='*60}\n")
    
    # Load data
    print("1️⃣ Loading treatment subset data...")
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
    
    # Co-occurrence analysis
    print("\n6️⃣ Computing keyword co-occurrence patterns...")
    print("   Creating boolean matrices...")

    # Initialize boolean matrices
    emergency_matrix = np.zeros((len(df), len(emergency_keywords)), dtype=bool)
    treatment_matrix = np.zeros((len(df), len(treatment_keywords)), dtype=bool)

    # Pre-process text
    print("   Pre-processing text...")
    df['clean_text_lower'] = df['clean_text'].fillna('').str.lower()

    # Fill emergency matrix with progress bar
    print("   Processing emergency keywords...")
    for i, keyword in enumerate(tqdm(emergency_keywords, desc="Emergency keywords")):
        pattern = r'\b' + re.escape(keyword) + r'\b'
        try:
            emergency_matrix[:, i] = df['clean_text_lower'].str.contains(
                pattern, 
                regex=True, 
                na=False
            ).values
        except Exception as e:
            print(f"   Warning: Error processing keyword '{keyword}': {str(e)}")

    # Fill treatment matrix with progress bar
    print("   Processing treatment keywords...")
    for i, keyword in enumerate(tqdm(treatment_keywords, desc="Treatment keywords")):
        pattern = r'\b' + re.escape(keyword) + r'\b'
        try:
            treatment_matrix[:, i] = df['clean_text_lower'].str.contains(
                pattern, 
                regex=True, 
                na=False
            ).values
        except Exception as e:
            print(f"   Warning: Error processing keyword '{keyword}': {str(e)}")

    # Compute co-occurrence using matrix multiplication
    print("   Computing co-occurrence matrix...")
    cooc_matrix = emergency_matrix.T @ treatment_matrix

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
                    'percentage': float(count / total_records * 100)
                })

    # Sort and store results
    cooccurrence_pairs.sort(key=lambda x: x['cooccurrence_count'], reverse=True)
    stats['cooccurrence_analysis'] = cooccurrence_pairs[:20]  # Top 20 pairs

    print(f"   Found {len(cooccurrence_pairs)} co-occurrence pairs")
    print("   Top 5 co-occurrence pairs:")
    for i, pair in enumerate(cooccurrence_pairs[:5]):
        print(f"     {i+1}. {pair['emergency_keyword']} + {pair['treatment_keyword']}: {pair['cooccurrence_count']} ({pair['percentage']:.1f}%)")
    
    # Path B validation metrics
    print("\n7️⃣ Validating Path B strategy effectiveness...")
    
    # Calculate keyword density
    emergency_density = []
    treatment_density = []
    
    for _, row in df.iterrows():
        text = str(row['clean_text']).lower()
        em_matches = sum(1 for kw in emergency_keywords if kw.lower() in text)
        tr_matches = sum(1 for kw in treatment_keywords if kw.lower() in text)
        
        emergency_density.append(em_matches)
        treatment_density.append(tr_matches)
    
    df['emergency_keyword_density'] = emergency_density
    df['treatment_keyword_density'] = treatment_density
    
    stats['path_b_validation'] = {
        'avg_emergency_density': float(np.mean(emergency_density)),
        'avg_treatment_density': float(np.mean(treatment_density)),
        'high_density_records': int(sum(1 for ed, td in zip(emergency_density, treatment_density) if ed >= 2 and td >= 2)),
        'precision_estimate': float(sum(1 for ed, td in zip(emergency_density, treatment_density) if ed >= 1 and td >= 1) / total_records)
    }
    
    print(f"   Average emergency keyword density: {stats['path_b_validation']['avg_emergency_density']:.2f}")
    print(f"   Average treatment keyword density: {stats['path_b_validation']['avg_treatment_density']:.2f}")
    print(f"   High-density records (≥2 each): {stats['path_b_validation']['high_density_records']}")
    print(f"   Precision estimate: {stats['path_b_validation']['precision_estimate']:.2f}")
    
    # Condition mapping candidates
    print("\n8️⃣ Preparing condition mapping candidates...")
    
    # Group emergency keywords by potential conditions
    condition_candidates = {}
    for pair in cooccurrence_pairs[:10]:  # Top 10 pairs
        em_kw = pair['emergency_keyword']
        tr_kw = pair['treatment_keyword']
        
        # Simple condition inference (can be enhanced later)
        if any(cardiac_term in em_kw.lower() for cardiac_term in ['mi', 'cardiac', 'heart', 'chest']):
            condition = 'cardiac'
        elif any(resp_term in em_kw.lower() for resp_term in ['respiratory', 'breathing', 'lung', 'dyspnea']):
            condition = 'respiratory'
        elif any(neuro_term in em_kw.lower() for neuro_term in ['stroke', 'seizure', 'consciousness']):
            condition = 'neurological'
        else:
            condition = 'general'
        
        if condition not in condition_candidates:
            condition_candidates[condition] = []
        
        condition_candidates[condition].append({
            'emergency_keyword': em_kw,
            'treatment_keyword': tr_kw,
            'strength': pair['cooccurrence_count']
        })
    
    stats['condition_mapping_candidates'] = condition_candidates
    
    # Visualization
    print("\n9️⃣ Generating visualizations...")
    output_plots = output_dir / "plots"
    output_plots.mkdir(parents=True, exist_ok=True)
    
    # 1. Dual keyword distribution
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    
    # Emergency keywords in treatment subset
    em_counts = list(stats['emergency_keyword_stats'].values())
    em_labels = list(stats['emergency_keyword_stats'].keys())
    ax1.bar(range(len(em_labels)), em_counts)
    ax1.set_title('Emergency Keywords in Treatment Subset')
    ax1.set_xlabel('Emergency Keywords')
    ax1.set_ylabel('Document Count')
    ax1.tick_params(axis='x', rotation=45, labelsize=8)
    ax1.set_xticks(range(len(em_labels)))
    ax1.set_xticklabels(em_labels, ha='right')
    
    # Treatment keywords
    tr_counts = list(stats['treatment_keyword_stats'].values())
    tr_labels = list(stats['treatment_keyword_stats'].keys())
    ax2.bar(range(len(tr_labels)), tr_counts)
    ax2.set_title('Treatment Keywords Distribution')
    ax2.set_xlabel('Treatment Keywords')
    ax2.set_ylabel('Document Count')
    ax2.tick_params(axis='x', rotation=45, labelsize=8)
    ax2.set_xticks(range(len(tr_labels)))
    ax2.set_xticklabels(tr_labels, ha='right')
    
    plt.tight_layout()
    plt.savefig(output_plots / "dual_keyword_distribution.png", bbox_inches='tight', dpi=300)
    plt.close()
    
    # 2. Co-occurrence heatmap (top pairs)
    if len(cooccurrence_pairs) > 0:
        top_pairs = cooccurrence_pairs[:15]  # Top 15 for readability
        cooc_matrix = np.zeros((len(set([p['emergency_keyword'] for p in top_pairs])), 
                               len(set([p['treatment_keyword'] for p in top_pairs]))))
        
        em_unique = list(set([p['emergency_keyword'] for p in top_pairs]))
        tr_unique = list(set([p['treatment_keyword'] for p in top_pairs]))
        
        for pair in top_pairs:
            i = em_unique.index(pair['emergency_keyword'])
            j = tr_unique.index(pair['treatment_keyword'])
            cooc_matrix[i, j] = pair['cooccurrence_count']
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(cooc_matrix, 
                   xticklabels=tr_unique, 
                   yticklabels=em_unique,
                   annot=True, 
                   fmt='g',
                   cmap='YlOrRd')
        plt.title('Emergency-Treatment Keywords Co-occurrence Heatmap')
        plt.xlabel('Treatment Keywords')
        plt.ylabel('Emergency Keywords')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig(output_plots / "cooccurrence_heatmap.png", bbox_inches='tight', dpi=300)
        plt.close()
    
    # 3. Text length distribution
    plt.figure(figsize=(10, 6))
    df['text_length'].hist(bins=50, alpha=0.7)
    plt.title('Text Length Distribution in Treatment Subset')
    plt.xlabel('Text Length (characters)')
    plt.ylabel('Frequency')
    plt.axvline(avg_length, color='red', linestyle='--', label=f'Average: {avg_length:.0f}')
    plt.legend()
    plt.savefig(output_plots / "text_length_distribution.png", bbox_inches='tight')
    plt.close()
    
    # 4. Keyword density scatter plot
    plt.figure(figsize=(10, 8))
    plt.scatter(df['emergency_keyword_density'], df['treatment_keyword_density'], alpha=0.6)
    plt.xlabel('Emergency Keyword Density')
    plt.ylabel('Treatment Keyword Density')
    plt.title('Emergency vs Treatment Keyword Density')
    plt.grid(True, alpha=0.3)
    plt.savefig(output_plots / "keyword_density_scatter.png", bbox_inches='tight')
    plt.close()
    
    # Save comprehensive statistics
    print("\n🔟 Saving analysis results...")
    stats_dir = output_dir / "stats"
    stats_dir.mkdir(parents=True, exist_ok=True)
    
    with open(stats_dir / "treatment_analysis_comprehensive.json", 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    # Save co-occurrence pairs as CSV for easy review
    if cooccurrence_pairs:
        cooc_df = pd.DataFrame(cooccurrence_pairs)
        cooc_df.to_csv(stats_dir / "cooccurrence_pairs.csv", index=False)
    
    print(f"✅ Treatment subset analysis complete!")
    print(f"   Results saved to: {output_dir}")
    print(f"   Plots: {output_plots}")
    print(f"   Statistics: {stats_dir}")
    
    return stats

if __name__ == "__main__":
    # Configuration
    treatment_file = "../dataset/emergency_treatment/emergency_treatment_subset.csv"
    emergency_keywords = "../keywords/emergency_keywords.txt"
    treatment_keywords = "../keywords/treatment_keywords.txt"
    output_directory = "../analysis_treatment"
    
    # Run analysis
    results = analyze_treatment_subset(
        treatment_file, 
        emergency_keywords, 
        treatment_keywords, 
        output_directory
    ) 