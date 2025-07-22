# /scripts/data_explorer.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import json

def analyze_subset(file_path, keywords_path, output_dir="analysis"):
    """分析子集數據質量和分布"""
    print(f"\n{'='*50}")
    print(f"開始分析數據集: {file_path}")
    print(f"使用關鍵詞文件: {keywords_path}")
    print(f"輸出目錄: {output_dir}")
    print(f"{'='*50}\n")
    
    # 載入數據
    print("1️⃣ 載入數據...")
    df = pd.read_csv(file_path)
    output_dir = Path(output_dir)
    
    # 1. 基本統計
    print("\n2️⃣ 計算基本統計...")
    print(f"總記錄數: {len(df)}")
    df['text_length'] = df['clean_text'].str.len()
    print(f"平均文本長度: {df['text_length'].mean():.2f}")
    
    # 2. 關鍵字分析
    print("\n3️⃣ 進行關鍵字分析...")
    with open(keywords_path, 'r') as f:
        keywords = [line.strip() for line in f if line.strip()]
    print(f"載入了 {len(keywords)} 個關鍵字")
    
    keyword_stats = {}
    for keyword in keywords:
        count = df['clean_text'].str.contains(keyword, case=False).sum()
        keyword_stats[keyword] = count
        print(f"  - {keyword}: {count} 條記錄")
    
    # 3. 可視化
    print("\n4️⃣ 生成可視化...")
    output_path = Path(output_dir) / "plots"
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"圖表將保存在: {output_path}")
    
    # 3.1 關鍵詞分布圖
    print("  - 生成關鍵詞分布圖...")
    plt.figure(figsize=(15, 8))
    plt.bar(keyword_stats.keys(), keyword_stats.values())
    plt.xticks(rotation=45, ha='right')
    plt.title('關鍵詞匹配分布')
    plt.xlabel('關鍵詞')
    plt.ylabel('匹配數量')
    plt.savefig(output_path / "keyword_distribution_emergency_subset.png", bbox_inches='tight')
    plt.close()
    
    # 3.2 文本長度分布
    print("  - 生成文本長度分布圖...")
    plt.figure(figsize=(10, 6))
    df['text_length'].hist(bins=50)
    plt.title('文本長度分布')
    plt.xlabel('文本長度')
    plt.ylabel('頻率')
    plt.savefig(output_path / "text_length_dist.png", bbox_inches='tight')
    plt.close()
    
    # 3.3 關鍵詞共現分析
    print("  - 生成關鍵詞共現熱力圖...")
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
    
    # 4. 保存統計數據
    print("\n5️⃣ 保存統計數據...")
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
    stats_file = stats_path / "analysis_stats_emergency_subset.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"統計數據已保存到: {stats_file}")
    
    print(f"\n✅ 分析完成！所有結果已保存到 {output_dir} 目錄")

if __name__ == "__main__":
    # 設定文件路徑
    emergency_subset = "../dataset/emergency/emergency_subset.csv"
    emergency_keywords = "../keywords/emergency_keywords.txt"
    output_dir = "../analysis"
    
    # 執行分析
    analyze_subset(emergency_subset, emergency_keywords, output_dir)