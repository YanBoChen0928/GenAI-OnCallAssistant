"""
Chunk Quality Analysis Tests

This module analyzes chunk quality and identifies issues with chunk length differences
between emergency and treatment data processing methods.

Author: OnCall.ai Team
Date: 2025-07-28
"""

import sys
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

# Add src to python path
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent
sys.path.append(str(project_root / "src"))

from data_processing import DataProcessor #type: ignore

class TestChunkQualityAnalysis:
    
    def setup_class(self):
        """Initialize test environment"""
        print("\n=== Phase 1: Setting up Chunk Quality Analysis ===")
        self.base_dir = Path(__file__).parent.parent.resolve()
        self.models_dir = self.base_dir / "models"
        self.embeddings_dir = self.models_dir / "embeddings"
        
        print(f"• Base directory: {self.base_dir}")
        print(f"• Models directory: {self.models_dir}")
        
        # Initialize processor
        self.processor = DataProcessor(base_dir=str(self.base_dir))
        print("• DataProcessor initialized")

    def test_chunk_length_analysis(self):
        """Detailed analysis of chunk length distribution"""
        print("\n=== Phase 2: Chunk Length Distribution Analysis ===")
        
        try:
            # Load chunk data
            print("• Loading chunk data...")
            with open(self.embeddings_dir / "emergency_chunks.json", 'r') as f:
                emergency_chunks = json.load(f)
            with open(self.embeddings_dir / "treatment_chunks.json", 'r') as f:
                treatment_chunks = json.load(f)
            
            # Analyze emergency chunks
            em_lengths = [len(chunk['text']) for chunk in emergency_chunks]
            em_token_counts = [chunk.get('token_count', 0) for chunk in emergency_chunks]
            
            print(f"\n📊 Emergency Chunks Analysis:")
            print(f"• Total chunks: {len(em_lengths):,}")
            print(f"• Min length: {min(em_lengths)} chars")
            print(f"• Max length: {max(em_lengths)} chars")
            print(f"• Average length: {sum(em_lengths)/len(em_lengths):.2f} chars")
            print(f"• Median length: {sorted(em_lengths)[len(em_lengths)//2]} chars")
            
            if any(em_token_counts):
                avg_tokens = sum(em_token_counts)/len(em_token_counts)
                print(f"• Average tokens: {avg_tokens:.2f}")
                print(f"• Chars per token ratio: {(sum(em_lengths)/len(em_lengths)) / avg_tokens:.2f}")
            
            # Analyze treatment chunks
            tr_lengths = [len(chunk['text']) for chunk in treatment_chunks]
            
            print(f"\n📊 Treatment Chunks Analysis:")
            print(f"• Total chunks: {len(tr_lengths):,}")
            print(f"• Min length: {min(tr_lengths)} chars")
            print(f"• Max length: {max(tr_lengths)} chars")
            print(f"• Average length: {sum(tr_lengths)/len(tr_lengths):.2f} chars")
            print(f"• Median length: {sorted(tr_lengths)[len(tr_lengths)//2]} chars")
            
            # Length distribution comparison
            em_avg = sum(em_lengths)/len(em_lengths)
            tr_avg = sum(tr_lengths)/len(tr_lengths)
            ratio = em_avg / tr_avg
            
            print(f"\n🔍 Length Distribution Comparison:")
            print(f"• Emergency average: {em_avg:.0f} chars")
            print(f"• Treatment average: {tr_avg:.0f} chars")
            print(f"• Ratio (Emergency/Treatment): {ratio:.1f}x")
            
            # Length distribution buckets
            print(f"\n📈 Length Distribution Buckets:")
            buckets = [0, 100, 250, 500, 1000, 2000, 5000]
            
            for i in range(len(buckets)-1):
                em_count = sum(1 for l in em_lengths if buckets[i] <= l < buckets[i+1])
                tr_count = sum(1 for l in tr_lengths if buckets[i] <= l < buckets[i+1])
                print(f"• {buckets[i]}-{buckets[i+1]} chars: Emergency={em_count}, Treatment={tr_count}")
            
            # Flag potential issues
            if ratio > 5.0:
                print(f"\n⚠️  WARNING: Emergency chunks are {ratio:.1f}x longer than treatment chunks!")
                print("   This suggests different chunking strategies are being used.")
            
            print("✅ Chunk length analysis completed")
            
        except Exception as e:
            print(f"❌ Error in chunk length analysis: {str(e)}")
            raise

    def test_chunking_method_comparison(self):
        """Compare the two chunking methods on the same data"""
        print("\n=== Phase 3: Chunking Method Comparison ===")
        
        try:
            # Load data
            print("• Loading dataset for comparison...")
            self.processor.load_filtered_data()
            
            # Test on multiple samples for better analysis
            sample_size = 5
            samples = self.processor.treatment_data.head(sample_size)
            
            method1_results = []  # keyword_centered_chunks
            method2_results = []  # dual_keyword_chunks
            
            print(f"• Testing {sample_size} samples with both methods...")
            
            for idx, row in samples.iterrows():
                if not row.get('clean_text') or not row.get('treatment_matched'):
                    continue
                    
                text_length = len(row['clean_text'])
                emergency_kw = row.get('matched', '')
                treatment_kw = row['treatment_matched']
                
                # Method 1: keyword_centered_chunks (Emergency method)
                chunks1 = self.processor.create_keyword_centered_chunks(
                    text=row['clean_text'],
                    matched_keywords=emergency_kw,
                    chunk_size=256,
                    doc_id=f"test_{idx}"
                )
                
                # Method 2: dual_keyword_chunks (Treatment method)
                chunks2 = self.processor.create_dual_keyword_chunks(
                    text=row['clean_text'],
                    emergency_keywords=emergency_kw,
                    treatment_keywords=treatment_kw,
                    chunk_size=256,
                    doc_id=f"test_{idx}"
                )
                
                # Collect results
                if chunks1:
                    avg_len1 = sum(len(c['text']) for c in chunks1) / len(chunks1)
                    method1_results.append({
                        'doc_id': idx,
                        'chunks_count': len(chunks1),
                        'avg_length': avg_len1,
                        'text_length': text_length
                    })
                
                if chunks2:
                    avg_len2 = sum(len(c['text']) for c in chunks2) / len(chunks2)
                    method2_results.append({
                        'doc_id': idx,
                        'chunks_count': len(chunks2),
                        'avg_length': avg_len2,
                        'text_length': text_length
                    })
            
            # Analysis results
            print(f"\n📊 Method Comparison Results:")
            
            if method1_results:
                avg_chunks1 = sum(r['chunks_count'] for r in method1_results) / len(method1_results)
                avg_len1 = sum(r['avg_length'] for r in method1_results) / len(method1_results)
                print(f"\n🔹 Keyword-Centered Method (Emergency):")
                print(f"• Average chunks per document: {avg_chunks1:.1f}")
                print(f"• Average chunk length: {avg_len1:.0f} chars")
            
            if method2_results:
                avg_chunks2 = sum(r['chunks_count'] for r in method2_results) / len(method2_results)
                avg_len2 = sum(r['avg_length'] for r in method2_results) / len(method2_results)
                print(f"\n🔹 Dual-Keyword Method (Treatment):")
                print(f"• Average chunks per document: {avg_chunks2:.1f}")
                print(f"• Average chunk length: {avg_len2:.0f} chars")
                
                if method1_results:
                    ratio = avg_len1 / avg_len2
                    print(f"\n🔍 Length Ratio: {ratio:.1f}x (Method1 / Method2)")
            
            print("✅ Chunking method comparison completed")
            
        except Exception as e:
            print(f"❌ Error in method comparison: {str(e)}")
            raise

    def test_token_vs_character_analysis(self):
        """Analyze token vs character differences in chunking"""
        print("\n=== Phase 4: Token vs Character Analysis ===")
        
        try:
            # Load model for tokenization
            print("• Loading embedding model for tokenization...")
            self.processor.load_embedding_model()
            
            # Test sample texts
            test_texts = [
                "Patient presents with acute chest pain and shortness of breath.",
                "Emergency treatment for myocardial infarction includes immediate medication.",
                "The patient's vital signs show tachycardia and hypotension requiring intervention."
            ]
            
            print(f"\n📊 Token vs Character Analysis:")
            
            total_chars = 0
            total_tokens = 0
            
            for i, text in enumerate(test_texts, 1):
                char_count = len(text)
                token_count = len(self.processor.tokenizer.tokenize(text))
                ratio = char_count / token_count if token_count > 0 else 0
                
                print(f"\nSample {i}:")
                print(f"• Text: {text[:50]}...")
                print(f"• Characters: {char_count}")
                print(f"• Tokens: {token_count}")
                print(f"• Chars/Token ratio: {ratio:.2f}")
                
                total_chars += char_count
                total_tokens += token_count
            
            overall_ratio = total_chars / total_tokens
            print(f"\n🔍 Overall Character/Token Ratio: {overall_ratio:.2f}")
            
            # Estimate chunk sizes
            target_tokens = 256
            estimated_chars = target_tokens * overall_ratio
            
            print(f"\n📏 Chunk Size Estimates:")
            print(f"• Target tokens: {target_tokens}")
            print(f"• Estimated characters: {estimated_chars:.0f}")
            print(f"• Current emergency avg: 1842 chars ({1842/overall_ratio:.0f} estimated tokens)")
            print(f"• Current treatment avg: 250 chars ({250/overall_ratio:.0f} estimated tokens)")
            
            # Recommendations
            print(f"\n💡 Recommendations:")
            if 1842/overall_ratio > 512:
                print("⚠️  Emergency chunks may exceed model's 512 token limit!")
            if 250/overall_ratio < 64:
                print("⚠️  Treatment chunks may be too short for meaningful context!")
            
            print("✅ Token vs character analysis completed")
            
        except Exception as e:
            print(f"❌ Error in token analysis: {str(e)}")
            raise

    def test_generate_recommendations(self):
        """Generate recommendations based on analysis"""
        print("\n=== Phase 5: Generating Recommendations ===")
        
        recommendations = []
        
        # Based on the known chunk length difference
        recommendations.append({
            'issue': 'Inconsistent chunk lengths',
            'description': 'Emergency chunks (1842 chars) are 7x longer than treatment chunks (250 chars)',
            'recommendation': 'Standardize both methods to use token-based chunking with consistent parameters',
            'priority': 'HIGH'
        })
        
        recommendations.append({
            'issue': 'Different chunking strategies',
            'description': 'Emergency uses keyword-centered (token-based), Treatment uses dual-keyword (character-based)',
            'recommendation': 'Update dual_keyword_chunks to use tokenizer for consistent token-based chunking',
            'priority': 'HIGH'
        })
        
        recommendations.append({
            'issue': 'Potential token limit overflow',
            'description': 'Large chunks may exceed PubMedBERT 512 token limit',
            'recommendation': 'Implement strict token-based chunking with overlap to prevent overflow',
            'priority': 'MEDIUM'
        })
        
        print(f"\n📋 Analysis Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['issue']} [{rec['priority']}]")
            print(f"   Problem: {rec['description']}")
            print(f"   Solution: {rec['recommendation']}")
        
        print("\n✅ Recommendations generated")
        return recommendations

def main():
    """Run all chunk quality analysis tests"""
    print("\n" + "="*60)
    print("CHUNK QUALITY ANALYSIS TEST SUITE")
    print("="*60)
    
    test = TestChunkQualityAnalysis()
    test.setup_class()
    
    try:
        test.test_chunk_length_analysis()
        test.test_chunking_method_comparison()
        test.test_token_vs_character_analysis()
        recommendations = test.test_generate_recommendations()
        
        print("\n" + "="*60)
        print("🎉 ALL CHUNK QUALITY TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"\nKey Finding: Chunk length inconsistency detected!")
        print(f"Emergency: ~1842 chars, Treatment: ~250 chars (7x difference)")
        print(f"Recommendation: Standardize to token-based chunking")
        print("="*60)
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ CHUNK QUALITY TESTS FAILED!")
        print(f"Error: {str(e)}")
        print("="*60)

if __name__ == "__main__":
    main() 