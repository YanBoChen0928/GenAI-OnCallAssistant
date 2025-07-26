import pandas as pd
import re
from pathlib import Path
import json

def test_special_terms_matching():
    """
    Test special medical term matching logic
    """
    # Test cases for different scenarios
    test_cases = {
        "x-ray variants": [
            "Patient needs an x-ray of the chest",
            "Ordered chest xray",
            "X ray shows pneumonia",
            "XRAY negative"
        ],
        "ct-scan variants": [
            "CT scan reveals nodule",
            "CT-scan indicates mass",
            "Requires ctscan urgently",
            "CTSCAN of abdomen"
        ],
        "point-of-care variants": [
            "Point-of-care testing needed",
            "Point of care ultrasound",
            "POC testing results"
        ],
        "mixed cases": [
            "Ordered both x-ray and CT scan",
            "XRAY and CTSCAN negative",
            "Multiple point-of-care tests with x-ray"
        ],
        "negative cases": [
            "No imaging mentioned",
            "Regular examination only",
            "Laboratory tests pending"
        ]
    }
    
    # Special terms dictionary (from keyword_Match_Clean_for_subset_filter.txt)
    special_terms = {
        'x-ray': ['x-ray', 'x ray', 'xray'],
        'ct-scan': ['ct-scan', 'ct scan', 'ctscan'],
        'point-of-care': ['point-of-care', 'point of care']
    }
    
    # Create test DataFrame
    test_df = pd.DataFrame({
        'clean_text': [text for cases in test_cases.values() for text in cases],
        'category': [cat for cat, texts in test_cases.items() for _ in texts]
    })
    
    # Process keywords
    processed_keywords = []
    for term, variants in special_terms.items():
        processed_keywords.extend(variants)
    
    # Create regex pattern
    pattern = r"\b(?:" + "|".join(map(re.escape, processed_keywords)) + r")\b"
    
    # Apply matching logic
    test_df['matched'] = (
        test_df['clean_text']
        .fillna("")
        .str.findall(pattern, flags=re.IGNORECASE)
        .apply(lambda lst: "|".join(lst) if lst else "")
    )
    
    return test_df

def test_basic_matching():
    """
    Test basic keyword matching functionality
    """
    # Basic test cases
    test_cases = {
        "simple matches": [
            "Emergency treatment required",
            "Acute condition observed",
            "Urgent care needed"
        ],
        "case variations": [
            "EMERGENCY situation",
            "Acute RESPIRATORY failure",
            "URgent surgical intervention"
        ],
        "multiple matches": [
            "Emergency treatment for acute condition",
            "Urgent care in emergency department",
            "Acute respiratory emergency"
        ],
        "partial words": [
            "Non-emergency situation",
            "Subacute condition",
            "Emergency-related"
        ]
    }
    
    # Create test DataFrame
    test_df = pd.DataFrame({
        'clean_text': [text for cases in test_cases.values() for text in cases],
        'category': [cat for cat, texts in test_cases.items() for _ in texts]
    })
    
    # Test keywords
    test_keywords = ['emergency', 'acute', 'urgent']
    pattern = r"\b(?:" + "|".join(map(re.escape, test_keywords)) + r")\b"
    
    # Apply matching logic
    test_df['matched'] = (
        test_df['clean_text']
        .fillna("")
        .str.findall(pattern, flags=re.IGNORECASE)
        .apply(lambda lst: "|".join(lst) if lst else "")
    )
    
    return test_df

def save_test_results(results_dict):
    """
    Save test results to JSON file
    """
    output_dir = Path("../analysis")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "keyword_matching_test_results.json"
    
    # Convert DataFrame results to dictionary
    for key, df in results_dict.items():
        results_dict[key] = df.to_dict(orient='records')
    
    with open(output_file, 'w') as f:
        json.dump(results_dict, f, indent=2)
    
    print(f"Results saved to: {output_file}")

def run_tests():
    """
    Run all tests and output results
    """
    print("🧪 Running keyword matching tests...")
    
    # Run tests
    special_terms_results = test_special_terms_matching()
    basic_matching_results = test_basic_matching()
    
    # Print results
    print("\n📊 Special Terms Matching Results:")
    for category in special_terms_results['category'].unique():
        print(f"\n{category}:")
        subset = special_terms_results[special_terms_results['category'] == category]
        for _, row in subset.iterrows():
            print(f"Text: {row['clean_text']}")
            print(f"Matched: {row['matched'] or 'No matches'}")
            print("-" * 50)
    
    print("\n📊 Basic Matching Results:")
    for category in basic_matching_results['category'].unique():
        print(f"\n{category}:")
        subset = basic_matching_results[basic_matching_results['category'] == category]
        for _, row in subset.iterrows():
            print(f"Text: {row['clean_text']}")
            print(f"Matched: {row['matched'] or 'No matches'}")
            print("-" * 50)
    
    # Save results
    results_dict = {
        'special_terms_matching': special_terms_results,
        'basic_matching': basic_matching_results
    }
    save_test_results(results_dict)

if __name__ == "__main__":
    run_tests() 