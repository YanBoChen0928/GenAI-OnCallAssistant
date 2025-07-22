# filter_guidelines.py

from datasets import load_dataset
import pandas as pd
import os

# ✅ 你信任的來源來源縮寫（Hugging Face dataset 中的 source 欄位）
approved_sources = ["cco", "cdc", "cma", "icrc", "nice", "pubmed", "spor", "who", "wikidoc"]

# Step 1: 從 Hugging Face 載入資料集
print("⏳ 載入資料中...")
ds = load_dataset("epfl-llm/guidelines", split="train")

# Step 2: 依據 source 欄位進行過濾
print("🔍 篩選可信來源中...")
ds_filtered = ds.filter(lambda ex: ex["source"] in approved_sources)
print(f"✅ 篩選完成，總共 {len(ds_filtered)} 筆資料。")

# Step 3: 轉成 pandas DataFrame
print("📄 轉換為 DataFrame...")
df = ds_filtered.to_pandas()

# Step 4: 建立 dataset 資料夾（如果不存在）
os.makedirs("dataset", exist_ok=True)

# Step 5: 儲存為 JSONL 與 CSV 到 dataset/ 資料夾中
print("💾 儲存到 dataset/ 資料夾...")
df.to_json("dataset/guidelines_source_filtered.jsonl", orient="records", lines=True)
df.to_csv("dataset/guidelines_source_filtered.csv", index=False)

print("🎉 完成！已儲存來自可信來源的資料。")
