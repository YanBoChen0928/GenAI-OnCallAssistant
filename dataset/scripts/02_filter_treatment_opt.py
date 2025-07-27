import os
import re
import json
import pandas as pd
from pathlib import Path

class MedicalTermProcessor:
    def __init__(self):
        # Load treatment special terms from JSON
        keywords_dir = Path("../keywords")
        with open(keywords_dir / "special_terms_treatment.json", "r") as f:
            self.treatment_terms_by_category = json.load(f)
            
        # Flatten the nested structure for easy lookup
        self.treatment_special_terms = {}
        for category in self.treatment_terms_by_category.values():
            self.treatment_special_terms.update(category)
        
    def get_all_variants(self):
        """Get all term variants including special terms"""
        variants = []
        for term_list in self.treatment_special_terms.values():
            variants.extend(term_list)
        return variants

    def standardize_term(self, term: str) -> str:
        """Convert a term to its standard form if it's a variant"""
        term_lower = term.lower()
        for standard_term, variants in self.treatment_special_terms.items():
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

def load_keywords(path, processor):
    """Load and preprocess treatment keywords"""
    print(f"📥 Loading keywords from: {path}")
    
    # Load basic keywords
    with open(path, "r", encoding="utf-8") as f:
        basic_kws = [line.strip() for line in f if line.strip()]
    
    # Add special term variants
    special_kws = processor.get_all_variants()
    all_kws = list(set(basic_kws + special_kws))  # Remove duplicates
    
    print(f"   Loaded {len(all_kws)} keywords (including variants)")
    return all_kws

# Step 1: Read optimized emergency subset
print("1️⃣ Reading optimized emergency subset...")
emergency_path = "../dataset/emergency/emergency_subset_opt.jsonl"
df = pd.read_json(emergency_path, lines=True)
print(f"   Loaded {len(df)} emergency records")
print(f"   Contains emergency keywords in 'matched' column")

# Step 2: Load treatment keywords and match
print("2️⃣ Loading treatment keywords and matching...")
processor = MedicalTermProcessor()
keywords = load_keywords("../keywords/treatment_keywords.txt", processor)
pattern = r"\b(?:" + "|".join(map(re.escape, keywords)) + r")\b"

# Step 3: Process text and match keywords
print("3️⃣ Processing text and matching keywords...")
# Match treatment keywords and add metadata columns
df["treatment_matched"] = (
    df["clean_text"]
      .fillna("")  # Convert NaN to empty string
      .str.findall(pattern, flags=re.IGNORECASE)
      .apply(lambda matches: processor.process_matches(matches))  # Use new process_matches method
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

# Save with _opt suffix
subset.to_json(f"{out_dir}/emergency_treatment_subset_opt.jsonl", orient="records", lines=True)
subset.to_csv(f"{out_dir}/emergency_treatment_subset_opt.csv", index=False)

print(f"✅ Generated optimized treatment subset with {len(subset)} records")
print(f"   Saved in: {out_dir}")
print(f"   Contains both emergency and treatment keywords") 