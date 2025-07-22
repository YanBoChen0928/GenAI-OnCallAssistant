# /scripts/data_explorer.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  # 添加
import numpy as np     # 添加
from pathlib import Path
import json           # 添加

def analyze_subset(file_path, keywords_path, output_dir="analysis"):
    """分析子集數據質量和分布"""
    print(f"正在分析: {file_path}")
    
    # 載入數據
    df = pd.read_csv(file_path)
    output_dir = Path(output_dir)
    
    # 1. 基本統計 (保持原有的)
    print(f"總記錄數: {len(df)}")
    df['text_length'] = df['clean_text'].str.len()  # 移到這裡
    print(f"平均文本長度: {df['text_length'].mean():.2f}")
    
    # 2. 關鍵字分析 (保持原有的)
    with open(keywords_path, 'r') as f:
        keywords = [line.strip() for line in f if line.strip()]
    
    keyword_stats = {}
    for keyword in keywords:
        count = df['clean_text'].str.contains(keyword, case=False).sum()
        keyword_stats[keyword] = count
        print(f"{keyword}: {count} 條記錄")
    
    # 3. 可視化
    output_path = Path(output_dir) / "plots"
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 3.1 關鍵詞分布圖 (原有的)
    plt.figure(figsize=(15, 8))
    plt.bar(keyword_stats.keys(), keyword_stats.values())
    plt.xticks(rotation=45, ha='right')
    plt.title('關鍵詞匹配分布')
    plt.xlabel('關鍵詞')
    plt.ylabel('匹配數量')
    # TODO: change the name of the file to the name of the subset
    plt.savefig(output_path / "keyword_distribution_emergency_subset.png", bbox_inches='tight')
    plt.close()
    
    # 3.2 文本長度分布 (新增的)
    plt.figure(figsize=(10, 6))
    df['text_length'].hist(bins=50)
    plt.title('文本長度分布')
    plt.xlabel('文本長度')
    plt.ylabel('頻率')
    plt.savefig(output_path / "text_length_dist.png", bbox_inches='tight')
    plt.close()
    
    # 3.3 關鍵詞共現分析 (新增的)
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
    plt.title('關鍵詞共現熱力圖')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    # TODO: change the name of the file to the name of the subset
    plt.savefig(output_path / "keyword_cooccurrence_emergency_subset.png", bbox_inches='tight')
    plt.close()
    
    # 4. 保存統計數據 (擴展原有的)
    stats_path = Path(output_dir) / "stats"
    stats_path.mkdir(parents=True, exist_ok=True)
    
    stats = {
        '基本統計': {
            '總記錄數': len(df),
            '平均文本長度': float(df['text_length'].mean()),
            '文本長度分位數': df['text_length'].describe().to_dict()
        },
        '關鍵詞統計': keyword_stats
    }
    
    # TODO: change the name of the file to the name of the subset
    with open(stats_path / "analysis_stats_emergency_subset.json", 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)