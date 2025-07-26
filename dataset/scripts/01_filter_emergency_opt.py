import os
import re
import json
import pandas as pd
from pathlib import Path

class MedicalTermProcessor:
    def __init__(self):
        # Load emergency special terms from JSON
        keywords_dir = Path("../keywords")
        with open(keywords_dir / "special_terms_emergency.json", "r") as f:
            self.emergency_terms_by_category = json.load(f)
            
        # Flatten the nested structure for easy lookup
        self.emergency_special_terms = {}
        for category in self.emergency_terms_by_category.values():
            self.emergency_special_terms.update(category)
        
    def get_all_variants(self):
        """Get all term variants including special terms"""
        variants = []
        for term_list in self.emergency_special_terms.values():
            variants.extend(term_list)
        return variants

    def standardize_term(self, term: str) -> str:
        """Convert a term to its standard form if it's a variant"""
        term_lower = term.lower()
        for standard_term, variants in self.emergency_special_terms.items():
            if term_lower in [v.lower() for v in variants]:
                return standard_term
        return term

    def process_matches(self, matches: list) -> str:
        """Process matches to standardize terms and remove duplicates"""
        if not matches:
            return ""
        
        # Standardize terms
        standardized = [self.standardize_term(match) for match in matches]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_matches = []
        for term in standardized:
            if term.lower() not in seen:
                unique_matches.append(term)
                seen.add(term.lower())
                
        return "|".join(unique_matches)

# Function: Load keywords and print progress
def load_keywords(path, processor):
    print(f"📥 Loading keywords from: {path}")
    # Load basic keywords
    with open(path, "r", encoding="utf-8") as f:
        basic_kws = [line.strip() for line in f if line.strip()]
    
    # Add special term variants
    special_kws = processor.get_all_variants()
    all_kws = list(set(basic_kws + special_kws))  # Remove duplicates
    
    print(f"   Loaded {len(all_kws)} keywords (including variants)")
    return all_kws

# Step 1: Read source data
print("1️⃣ Reading source data...")
source_path = "../dataset/guidelines_source_filtered.jsonl"
df = pd.read_json(source_path, lines=True)
print(f"   Loaded {len(df)} records")

# Step 2: Load emergency keywords and match
print("2️⃣ Loading emergency keywords and matching...")
processor = MedicalTermProcessor()
keywords = load_keywords("../keywords/emergency_keywords.txt", processor)
pattern = r"\b(?:" + "|".join(map(re.escape, keywords)) + r")\b"

# Match keywords and add metadata columns
df["matched"] = (
    df["clean_text"]
      .fillna("")  # Convert NaN to empty string
      .str.findall(pattern, flags=re.IGNORECASE)
      .apply(lambda matches: processor.process_matches(matches))  # Use new process_matches method
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

# Save with _opt suffix to distinguish from original files
subset.to_json(f"{out_dir}/emergency_subset_opt.jsonl", orient="records", lines=True)
subset.to_csv(f"{out_dir}/emergency_subset_opt.csv", index=False)
print(f"✅ Complete! Generated emergency subset with {len(subset)} records, saved in `{out_dir}` with _opt suffix") 