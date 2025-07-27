# scripts/01_filter_emergency.py

import os
import re
import pandas as pd

# Function: Load keywords and print progress
def load_keywords(path):
    print(f"📥 Loading keywords from: {path}")
    with open(path, "r", encoding="utf-8") as f:
        kws = [line.strip() for line in f if line.strip()]
    print(f"   Loaded {len(kws)} keywords")
    return kws

# Step 1: Read source data
print("1️⃣ Reading source data...")
source_path = "../dataset/guidelines_source_filtered.jsonl"
df = pd.read_json(source_path, lines=True)
print(f"   Loaded {len(df)} records")

# Step 2: Load emergency keywords and match
print("2️⃣ Loading emergency keywords and matching...")
keywords = load_keywords("../keywords/emergency_keywords.txt")
pattern = r"\b(?:" + "|".join(keywords) + r")\b"  # Using non-capturing groups (?:...)

# Match keywords and add metadata columns
df["matched"] = (
    df["clean_text"]
      .fillna("")  # Convert NaN to empty string
      .str.findall(pattern, flags=re.IGNORECASE)
      .apply(lambda lst: "|".join(lst) if lst else "")
)
df["has_emergency"] = df["matched"].str.len() > 0

# Add metadata columns for future use
df["type"] = "emergency"  # Document type identifier
df["condition"] = ""      # Reserved for future condition mapping

# Calculate average matches
cnt_em = df["has_emergency"].sum()
avg_matches = (
    df[df["has_emergency"]]["matched"]
      .str.count(r"\|")  # Escape the pipe
      .add(1)
      .mean()
)

print(f"   Matched {cnt_em} emergency-related records")
print(f"   Average keywords per record: {avg_matches:.2f}")

# Step 3: Save emergency subset
print("3️⃣ Saving emergency subset...")
out_dir = "../dataset/emergency"
os.makedirs(out_dir, exist_ok=True)
subset = df[df["has_emergency"]]
subset.to_json(f"{out_dir}/emergency_subset.jsonl", orient="records", lines=True)
subset.to_csv(f"{out_dir}/emergency_subset.csv", index=False)
print(f"✅ Complete! Generated emergency subset with {len(subset)} records, saved in `{out_dir}`")
