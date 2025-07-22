# scripts/01_filter_emergency.py

import os
import re
import pandas as pd

# 工具函数：载入关键字并打印进度
def load_keywords(path):
    print(f"📥 读取关键字：{path}")
    with open(path, "r", encoding="utf-8") as f:
        kws = [line.strip() for line in f if line.strip()]
    print(f"   共载入 {len(kws)} 个关键字")
    return kws

# Step 1: 读取原始数据
print("1️⃣ 读取原始数据…")
source_path = "../dataset/guidelines_source_filtered.jsonl"
df = pd.read_json(source_path, lines=True)
print(f"   已读取 {len(df)} 条记录")

# Step 2: 载入急症关键字并匹配
print("2️⃣ 读取急症关键字并开始匹配…")
keywords = load_keywords("../keywords/emergency_keywords.txt")
pattern = r"\b(?:" + "|".join(keywords) + r")\b"  # 使用非捕獲組 (?:...)

# 匹配關鍵詞
df["matched"] = (
    df["clean_text"]
      .fillna("")  # 把 NaN 变成 ""
      .str.findall(pattern, flags=re.IGNORECASE)
      .apply(lambda lst: "|".join(lst) if lst else "")
)
df["has_emergency"] = df["matched"].str.len() > 0
cnt_em = df["has_emergency"].sum()

# 计算平均匹配数（注意转义）
avg_matches = (
    df[df["has_emergency"]]["matched"]
      .str.count(r"\|")  # 这里要转义
      .add(1)
      .mean()
)

print(f"   匹配到 {cnt_em} 条急症相关记录")
print(f"   其中平均每条记录包含 {avg_matches:.2f} 个关键词")

# Step 3: 保存急症子集
print("3️⃣ 保存急症子集…")
out_dir = "../dataset/emergency"
os.makedirs(out_dir, exist_ok=True)
subset = df[df["has_emergency"]]
subset.to_json(f"{out_dir}/emergency_subset.jsonl", orient="records", lines=True)
subset.to_csv(f"{out_dir}/emergency_subset.csv", index=False)
print(f"✅ 完成！已生成急症子集，共 {len(subset)} 条记录，保存在 `{out_dir}`")
