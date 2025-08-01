#!/usr/bin/env python3
"""OnCall AI - Medical RAG System

Main entry point for the medical RAG system.
"""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.demos.demo_runner import build_medical_rag_system, demo_rag_query, demo_all_strategies


def main():
    """Main program entry point."""
    try:
        # Build the system with chunk embeddings
        build_medical_rag_system(enable_chunk_embeddings=True)
        
        # Demo chunk-based retrieval
        print("\n" + "="*80)
        print("🧩 CHUNK-BASED RETRIEVAL DEMO")
        print("="*80)
        demo_rag_query("chest pain and shortness of breath", 
                      strategy="top_p", use_chunks=True, top_p=0.8)
        
    except KeyboardInterrupt:
        print("\n\n👋 User interrupted, program exiting")
    except Exception as e:
        print(f"\n❌ Program execution error: {e}")
        import traceback
        traceback.print_exc()


def interactive_demo():
    """Interactive demo mode."""
    print("🏥 OnCall AI - Interactive Demo Mode")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Build/rebuild system")
        print("2. Query with TOP-P strategy")
        print("3. Query with TOP-K strategy") 
        print("4. Compare all strategies")
        print("5. Custom query")
        print("6. Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == "1":
            build_medical_rag_system(enable_chunk_embeddings=True)
        elif choice == "2":
            query = input("Enter your query: ").strip()
            if query:
                demo_rag_query(query, strategy="top_p", use_chunks=True)
        elif choice == "3":
            query = input("Enter your query: ").strip()
            if query:
                demo_rag_query(query, strategy="top_k", use_chunks=True, top_k=3)
        elif choice == "4":
            query = input("Enter your query: ").strip()
            if query:
                demo_all_strategies(query)
        elif choice == "5":
            query = input("Enter your query: ").strip()
            strategy = input("Enter strategy (top_k/top_p/threshold): ").strip()
            if query and strategy:
                demo_rag_query(query, strategy=strategy, use_chunks=True)
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please select 1-6.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_demo()
    else:
        main()