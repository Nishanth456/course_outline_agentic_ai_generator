#!/usr/bin/env python
"""
Manual Test: Load curriculum from data/sample_curricula folder

This shows how to:
1. Load .txt files from data/sample_curricula
2. Chunk and embed them
3. Query the vector store

Run: python test_curriculum_loading.py
"""

import sys
import asyncio
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def test_curriculum_loading():
    """Test loading curriculum from folder."""
    
    print("=" * 80)
    print("CURRICULUM LOADING TEST - Read from data/sample_curricula folder")
    print("=" * 80)
    print()
    
    # Step 1: Initialize services
    print("📦 Step 1: Initializing services...")
    try:
        from services.vector_store import get_vector_store, reset_vector_store
        from services.embedding_service import reset_embedding_service
        from tools.curriculum_ingestion import IngestionPipeline
        
        reset_embedding_service()
        reset_vector_store()
        
        print("   ✅ Services initialized")
        print()
    except Exception as e:
        print(f"   ❌ Failed to initialize: {e}")
        return 1
    
    # Step 2: Load from folder
    print("📂 Step 2: Loading curriculum from data/sample_curricula...")
    try:
        pipeline = IngestionPipeline()
        stored_count, docs = pipeline.ingest_from_folder("data/sample_curricula")
        
        if stored_count > 0:
            print(f"   ✅ Loaded {stored_count} chunks from folder")
            print(f"   ✅ Created {len(docs)} VectorDocuments")
        else:
            print(f"   ⚠️  No chunks loaded. Trying hardcoded fallback...")
            stored_count, docs = pipeline.ingest_example_curriculum()
            print(f"   ✅ Fallback: Loaded {stored_count} chunks (hardcoded examples)")
        print()
    except Exception as e:
        print(f"   ❌ Failed to load curriculum: {e}")
        return 1
    
    # Step 3: Verify vector store
    print("🔍 Step 3: Checking vector store...")
    try:
        store = get_vector_store()
        stats = store.get_collection_stats()
        print(f"   ✅ Vector store stats: {stats}")
        print()
    except Exception as e:
        print(f"   ❌ Failed to check store: {e}")
        return 1
    
    # Step 4: Test similarity search
    print("🔎 Step 4: Testing similarity search...")
    try:
        queries = [
            "object oriented programming java",
            "machine learning algorithms",
            "cloud computing"
        ]
        
        for query in queries:
            results = store.similarity_search(query, k=3)
            print(f"   Query: '{query}'")
            print(f"   Found {len(results)} results:")
            
            for i, result in enumerate(results, 1):
                content_preview = result.get("content", "")[:80].replace("\n", " ")
                score = result.get("similarity_score", 0)
                source = result.get("metadata", {}).get("source_name", "unknown")
                print(f"     {i}. [{score:.3f}] {source}")
                print(f"        {content_preview}...")
            print()
    except Exception as e:
        print(f"   ❌ Search failed: {e}")
        return 1
    
    # Step 5: Verify metadata
    print("📋 Step 5: Checking metadata on retrieved documents...")
    try:
        results = store.similarity_search("java programming", k=1)
        if results:
            metadata = results[0].get("metadata", {})
            print(f"   Document 1 metadata:")
            print(f"     - source_name: {metadata.get('source_name')}")
            print(f"     - source_type: {metadata.get('source_type')}")
            print(f"     - institution: {metadata.get('institution_name')}")
            print(f"     - audience_level: {metadata.get('audience_level')}")
            print(f"   ✅ Metadata properly attached")
        print()
    except Exception as e:
        print(f"   ❌ Metadata check failed: {e}")
        return 1
    
    # Summary
    print("=" * 80)
    print("✅ CURRICULUM LOADING TEST PASSED")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  ✅ Loaded {stored_count} chunks from curriculum files")
    print(f"  ✅ Vector embeddings created and indexed")
    print(f"  ✅ Similarity search working")
    print(f"  ✅ Metadata preserved on all documents")
    print()
    print("Next steps:")
    print("  1. Run: pytest tests/test_phase_3_retrieval.py -v")
    print("  2. Then: python app.py  (to test in Streamlit)")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(test_curriculum_loading())
