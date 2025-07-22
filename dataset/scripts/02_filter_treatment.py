# scripts/02_filter_treatment.py

import os
import pandas as pd

# 工具函数：载入关键字
def load_keywords(path):
    print(f"📥 载入关键字：{path}")
    with open(path, "r") as f:
        kws = [line.strip() for line in f if line.strip()]
    print(f"   共载入 {len(kws)} 个关键字")
    return kws

# Step 1: 载入急症子集
print("1️⃣ 读取急症子集…")
emergency_path = "../dataset/emergency/emergency_subset.jsonl"
df = pd.read_json(emergency_path, lines=True)
print(f"   已读取 {len(df)} 条急症相关记录")

# Step 2: 载入处置/管理关键字并过滤
print("2️⃣ 读取处置/管理关键字并开始过滤…")
treatment_keywords = load_keywords("../keywords/treatment_keywords.txt")
pattern2 = "|".join(treatment_keywords)
df["has_treatment"] = df["clean_text"].str.contains(pattern2, case=False, na=False)
cnt_treat = df["has_treatment"].sum()
print(f"   匹配到 {cnt_treat} 条包含处置/管理描述的记录")

# Step 3: 保存急症+处置子集
print("3️⃣ 保存急症+处置子集…")
out_dir = "../dataset/emergency_treatment"
os.makedirs(out_dir, exist_ok=True)
subset2 = df[df["has_treatment"]]
subset2.to_json(f"{out_dir}/emergency_treatment_subset.jsonl", orient="records", lines=True)
subset2.to_csv(f"{out_dir}/emergency_treatment_subset.csv", index=False)
print(f"   已保存 {len(subset2)} 条记录到 `{out_dir}`")

print("✅ 完成！急症+处置子集已生成。")
