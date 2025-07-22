# scripts/02_filter_treatment.py

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

# Step 1: Load emergency subset
print("1️⃣ Reading emergency subset...")
emergency_path = "../dataset/emergency/emergency_subset.jsonl"
df = pd.read_json(emergency_path, lines=True)
print(f"   Loaded {len(df)} emergency records")

# Step 2: Load and apply treatment keywords
print("2️⃣ Loading treatment keywords and filtering...")
treatment_keywords = load_keywords("../keywords/treatment_keywords.txt")
pattern = r"\b(?:" + "|".join(treatment_keywords) + r")\b"

# Match treatment keywords and add metadata
df["treatment_matched"] = (
    df["clean_text"]
      .fillna("")
      .str.findall(pattern, flags=re.IGNORECASE)
      .apply(lambda lst: "|".join(lst) if lst else "")
)
df["has_treatment"] = df["treatment_matched"].str.len() > 0

# Add metadata columns for future use
df["type"] = "treatment"  # Document type identifier
df["condition"] = ""      # Reserved for future condition mapping

cnt_treat = df["has_treatment"].sum()
print(f"   Matched {cnt_treat} records with treatment information")

# Step 3: Save treatment subset
print("3️⃣ Saving treatment subset...")
out_dir = "../dataset/emergency_treatment"
os.makedirs(out_dir, exist_ok=True)
subset = df[df["has_treatment"]]
subset.to_json(f"{out_dir}/emergency_treatment_subset.jsonl", orient="records", lines=True)
subset.to_csv(f"{out_dir}/emergency_treatment_subset.csv", index=False)
print(f"✅ Complete! Generated treatment subset with {len(subset)} records, saved in `{out_dir}`")