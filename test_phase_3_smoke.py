#!/usr/bin/env python
"""
Phase 3 Smoke Test - Validates all components work
"""

import sys
import asyncio
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_all_components():
    """Test all Phase 3 components."""
    
    print("=" * 70)
    print("PHASE 3 SMOKE TEST - Validating All Components")
    print("=" * 70)
    print()
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Embeddings
    tests_total += 1
    try:
        from services.embedding_service import get_embedding_service, reset_embedding_service
        reset_embedding_service()
        service = get_embedding_service()
        emb = service.embed_text("Test embedding text for validation")
        assert len(emb) == 384
        assert all(isinstance(x, float) for x in emb)
        print("✅ Test 1: EmbeddingService works")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 1 FAILED: {e}")
    
    # Test 2: Vector Store
    tests_total += 1
    try:
        from services.vector_store import get_vector_store, reset_vector_store
        reset_vector_store()
        store = get_vector_store(force_new=True)
        assert store._initialized
        stats = store.get_collection_stats()
        assert "document_count" in stats
        print("✅ Test 2: VectorStore initializes correctly")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 2 FAILED: {e}")
    
    # Test 3: Vector Document Schema
    tests_total += 1
    try:
        from schemas.vector_document import VectorDocument, VectorDocumentMetadata, SourceType, UploadedBy
        metadata = VectorDocumentMetadata(
            institution_name="Test University",
            degree_level="undergraduate",
            subject_domain="computer_science",
            audience_level="beginner",
            depth_level="foundational",
            source_type=SourceType.EXAMPLE,
            uploaded_by=UploadedBy.SYSTEM,
        )
        doc = VectorDocument(
            content="This is test content for vector document validation. " * 10,
            metadata=metadata,
        )
        doc.validate()
        print("✅ Test 3: VectorDocument schema valid")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 3 FAILED: {e}")
    
    # Test 4: Ingestion Pipeline
    tests_total += 1
    try:
        from tools.curriculum_ingestion import IngestionPipeline
        reset_vector_store()
        pipeline = IngestionPipeline()
        count, docs = pipeline.ingest_example_curriculum()
        assert count > 0
        assert len(docs) > 0
        print(f"✅ Test 4: IngestionPipeline loaded {count} chunks")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 4 FAILED: {e}")
    
    # Test 5: Vector Search
    tests_total += 1
    try:
        from services.vector_store import get_vector_store
        store = get_vector_store()
        results = store.similarity_search("machine learning", k=5)
        assert len(results) > 0
        assert all("content" in r for r in results)
        print(f"✅ Test 5: Vector search found {len(results)} results")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 5 FAILED: {e}")
    
    # Test 6: Retrieval Agent
    tests_total += 1
    try:
        from schemas.user_input import UserInputSchema, AudienceLevel, AudienceCategory, LearningMode, DepthRequirement
        from schemas.execution_context import ExecutionContext
        from agents.retrieval_agent import RetrievalAgent
        
        user_input = UserInputSchema(
            course_title="Test Course",
            course_description="A test course",
            audience_level=AudienceLevel.BEGINNER,
            audience_category=AudienceCategory.TECHNICAL,
            learning_mode=LearningMode.ONLINE,
            depth_requirement=DepthRequirement.FOUNDATIONAL,
            duration_hours=40,
        )
        
        context = ExecutionContext(user_input=user_input, session_id="test")
        agent = RetrievalAgent()
        output = asyncio.run(agent.run(context))
        
        assert output is not None
        assert hasattr(output, "retrieved_chunks")
        assert 0.0 <= output.retrieval_confidence <= 1.0
        print(f"✅ Test 6: RetrievalAgent executed (confidence={output.retrieval_confidence:.2f})")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 6 FAILED: {e}")
    
    # Test 7: Orchestrator Integration
    tests_total += 1
    try:
        from agents.orchestrator import CourseOrchestratorAgent
        from schemas.user_input import UserInputSchema, AudienceLevel, AudienceCategory, LearningMode, DepthRequirement
        
        user_input = UserInputSchema(
            course_title="Integration Test Course",
            course_description="Testing orchestrator with Phase 3",
            audience_level=AudienceLevel.INTERMEDIATE,
            audience_category=AudienceCategory.TECHNICAL,
            learning_mode=LearningMode.HYBRID,
            depth_requirement=DepthRequirement.INTERMEDIATE,
            duration_hours=50,
        )
        
        orchestrator = CourseOrchestratorAgent()
        outline = asyncio.run(orchestrator.run(user_input.dict(), session_id="test"))
        
        assert outline is not None
        assert "modules" in outline or isinstance(outline, dict)
        print(f"✅ Test 7: Orchestrator integration works")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 7 FAILED: {e}")
    
    print()
    print("=" * 70)
    print(f"RESULTS: {tests_passed}/{tests_total} tests passed")
    print("=" * 70)
    
    if tests_passed == tests_total:
        print("🎉 All Phase 3 components validated successfully!")
        return 0
    else:
        print(f"⚠️  {tests_total - tests_passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(test_all_components())
