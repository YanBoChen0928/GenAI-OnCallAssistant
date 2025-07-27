# scripts/02_filter_treatment.py

import os
import re
import pandas as pd

def preprocess_keywords(keywords_file):
    """Load and preprocess treatment keywords"""
    print(f"📥 Loading keywords from: {keywords_file}")
    
    # Special medical terms with common variants
    special_terms = {
        'x-ray': ['x-ray', 'x ray', 'xray'],
        'ct-scan': ['ct-scan', 'ct scan', 'ctscan'],
        'point-of-care': ['point-of-care', 'point of care']
    }
    
    # Read and preprocess keywords
    with open(keywords_file, "r", encoding="utf-8") as f:
        keywords = [line.strip().lower() for line in f if line.strip()]
    
    # Process keywords and handle special terms
    processed_keywords = []
    for kw in keywords:
        if kw in special_terms:
            processed_keywords.extend(special_terms[kw])
        else:
            processed_keywords.append(kw)
    
    print(f"   Loaded {len(keywords)} base keywords")
    print(f"   Processed into {len(processed_keywords)} keyword variants")
    return processed_keywords

def create_regex_pattern(keywords):
    """Create compiled regex pattern with word boundaries"""
    pattern = r"\b(?:" + "|".join(map(re.escape, keywords)) + r")\b"
    return re.compile(pattern, re.IGNORECASE)

# Step 1: Read source data
print("1️⃣ Reading emergency subset...")
emergency_path = "../dataset/emergency/emergency_subset.jsonl"
df = pd.read_json(emergency_path, lines=True)
print(f"   Loaded {len(df)} emergency records")
print(f"   Contains emergency keywords in 'matched' column")

# Step 2: Load treatment keywords and match
print("2️⃣ Loading treatment keywords and matching...")
treatment_keywords = preprocess_keywords("../keywords/treatment_keywords.txt")
pattern = create_regex_pattern(treatment_keywords)

# Step 3: Process text and match keywords
print("3️⃣ Processing text and matching keywords...")
# Create lowercase version of text for matching
df['clean_text_lower'] = df['clean_text'].fillna('').str.lower()

# Match treatment keywords and add metadata columns
# Note: Preserving original 'matched' column from emergency subset
df["treatment_matched"] = (
    df["clean_text_lower"]
    .apply(lambda text: "|".join(pattern.findall(text)) or "")
)
df["has_treatment"] = df["treatment_matched"].str.len() > 0

# Add metadata columns for future use
df["type"] = "treatment"  # Document type identifier
df["condition"] = ""      # Reserved for future condition mapping

# Verify columns
print("   Verifying columns...")
print(f"   - Emergency keywords column (matched): {df['matched'].notna().sum()} records")
print(f"   - Treatment keywords column (treatment_matched): {df['treatment_matched'].notna().sum()} records")

# Calculate statistics
cnt_treat = df["has_treatment"].sum()
avg_matches = (
    df[df["has_treatment"]]["treatment_matched"]
      .str.count(r"\|")
      .add(1)
      .mean()
)

print(f"   Found {cnt_treat} treatment-related records")
print(f"   Average treatment keywords per record: {avg_matches:.2f}")

# Step 4: Save treatment subset
print("4️⃣ Saving treatment subset...")
out_dir = "../dataset/emergency_treatment"
os.makedirs(out_dir, exist_ok=True)

# Select records with treatment keywords
subset = df[df["has_treatment"]].copy()  # Use copy to avoid SettingWithCopyWarning

# Verify final subset columns
print("   Final subset columns:")
print(f"   - Emergency keywords (matched): {subset['matched'].notna().sum()} records")
print(f"   - Treatment keywords (treatment_matched): {subset['treatment_matched'].notna().sum()} records")

subset.to_json(f"{out_dir}/emergency_treatment_subset.jsonl", orient="records", lines=True)
subset.to_csv(f"{out_dir}/emergency_treatment_subset.csv", index=False)

print(f"✅ Generated treatment subset with {len(subset)} records")
print(f"   Saved in: {out_dir}")
print(f"   Contains both emergency and treatment keywords")