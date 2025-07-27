import pandas as pd

# 讀取剛剛下載並過濾後的 JSONL 檔案
df = pd.read_json("dataset/guidelines_source_filtered.jsonl", lines=True)

# 顯示各來源出現次數
print("📊 各來源出現次數：")
print(df["source"].value_counts())

# 驗證來源是否只有指定的 9 個
expected_sources = {"cco", "cdc", "cma", "icrc", "nice", "pubmed", "spor", "who", "wikidoc"}
actual_sources = set(df["source"].unique())

# 顯示驗證結果
if actual_sources == expected_sources:
    print("✅ 來源完全符合預期，沒有其他來源。")
else:
    print(f"❌ 發現未預期來源：{actual_sources - expected_sources}")
