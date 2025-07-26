import os
import re
import pandas as pd

# Medical term processor class for handling special terms
class MedicalTermProcessor:
    def __init__(self):
        # Emergency special terms mapping
        self.emergency_special_terms = {
            # Cardiac
            'mi': ['mi', 'm.i.', 'myocardial infarction', 'MI'],
            'acs': ['acs', 'ACS', 'acute coronary syndrome'],
            
            # Respiratory
            'ards': ['ards', 'ARDS', 'acute respiratory distress syndrome'],
            'respiratory_failure': ['respiratory failure', 'resp failure', 'RF'],
            
            # Neurological
            'loc': ['loc', 'LOC', 'loss of consciousness'],
            'cva': ['cva', 'CVA', 'stroke', 'cerebrovascular accident'],
            
            # Shock States
            'shock': ['shock', 'circulatory failure'],
            'septic_shock': ['septic shock', 'sepsis induced shock'],
            
            # Bleeding
            'gi_bleed': ['gi bleed', 'gi bleeding', 'gastrointestinal hemorrhage', 'GI hemorrhage'],
            'hemorrhage': ['hemorrhage', 'bleeding', 'blood loss'],
            
            # Vital Signs
            'hypotension': ['hypotension', 'low bp', 'low blood pressure'],
            'tachycardia': ['tachycardia', 'elevated heart rate', 'fast heart rate']
        }
        
    def get_all_variants(self):
        """Get all term variants including special terms"""
        variants = []
        for term_list in self.emergency_special_terms.values():
            variants.extend(term_list)
        return variants

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

# Save with _opt suffix to distinguish from original files
subset.to_json(f"{out_dir}/emergency_subset_opt.jsonl", orient="records", lines=True)
subset.to_csv(f"{out_dir}/emergency_subset_opt.csv", index=False)
print(f"✅ Complete! Generated emergency subset with {len(subset)} records, saved in `{out_dir}` with _opt suffix") 