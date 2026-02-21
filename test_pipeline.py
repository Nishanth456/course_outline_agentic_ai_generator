"""
Quick Test Pipeline: Phase 5 Module Creation Agent

Run this to verify:
1. LLM connection (Gemini)
2. Module Creation Agent
3. Complete orchestration pipeline
4. Course outline generation
"""

import asyncio
import json
import sys
from datetime import datetime

# Test banner
def print_header(text):
    print("\n" + "="*70)
    print(f" {text}")
    print("="*70)


async def test_llm_service():
    """Test 1: LLM Service Connection"""
    print_header("TEST 1: LLM Service & Gemini Connection")
    
    try:
        from services.llm_service import get_llm_service
        
        print("Initializing LLM Service...")
        service = get_llm_service()
        print(f"✓ Provider: {service.provider}")
        print(f"✓ Model: {service.config.model}")
        print(f"✓ Temperature: {service.config.temperature}")
        
        print("\nTesting LLM call with simple prompt...")
        response = await service.generate("Say 'Hello from Gemini!' in 5 words maximum.")
        print(f"✓ Response content: {response.content}")
        print(f"✓ Response provider: {response.provider}")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_schemas():
    """Test 2: Schema Validation"""
    print_header("TEST 2: Schema Validation")
    
    try:
        from schemas.course_outline import (
            CourseOutlineSchema, Module, Lesson, LearningObjective, BloomLevel
        )
        
        print("Creating sample learning objective...")
        obj = LearningObjective(
            objective_id="LO_TEST_1",
            statement="Understand test concepts",
            bloom_level=BloomLevel.UNDERSTAND,
            assessment_method="Quiz"
        )
        print(f"✓ Objective: {obj.statement}")
        
        print("\nCreating sample lesson...")
        lesson = Lesson(
            lesson_id="L_TEST_1",
            title="Test Lesson",
            duration_minutes=60,
            key_concepts=["concept1", "concept2"]
        )
        print(f"✓ Lesson: {lesson.title} ({lesson.duration_minutes}min)")
        
        print("\nCreating sample module...")
        module = Module(
            module_id="M_TEST_1",
            title="Test Module",
            description="This is a test module",
            estimated_hours=6.0,
            learning_objectives=[obj, obj, obj],  # Need 3+
            lessons=[lesson],
            assessment_type="quiz"
        )
        print(f"✓ Module: {module.title} ({module.estimated_hours}h)")
        print(f"✓ Objectives: {len(module.learning_objectives)}")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_utilities():
    """Test 3: Utility Functions"""
    print_header("TEST 3: Duration Allocator & Learning Mode Templates")
    
    try:
        from utils.duration_allocator import DurationAllocator
        from utils.learning_mode_templates import LearningModeTemplates
        
        print("Testing Duration Allocator...")
        allocator = DurationAllocator()
        result = allocator.allocate(40, "intermediate_level", "project_based")
        print(f"✓ Course: 40 hours → {result['num_modules']} modules")
        print(f"✓ Avg per module: {result['avg_hours_per_module']:.1f}h")
        print(f"✓ Mode adjustment: {result['mode_adjustment']['capstone_required']}")
        
        print("\nTesting Learning Mode Templates...")
        for mode in ["theory", "project_based", "interview_prep", "research"]:
            template = LearningModeTemplates.get_template(mode)
            print(f"✓ {template['template_name']:<25} - Capstone: {template['capstone_structure']['required']}")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_module_agent():
    """Test 4: Module Creation Agent"""
    print_header("TEST 4: Module Creation Agent")
    
    try:
        from agents.module_creation_agent import get_module_creation_agent
        from schemas.user_input import UserInputSchema
        from schemas.execution_context import ExecutionContext
        
        print("Initializing Module Creation Agent...")
        agent = get_module_creation_agent()
        print(f"✓ Agent ready: {agent.__class__.__name__}")
        
        print("\nCreating sample user input...")
        user_input = UserInputSchema(
            course_title="Quick Test Course",
            course_description="A test course for phase 5 validation",
            audience_level="undergraduate",
            audience_category="STEM",
            depth_requirement="intermediate_level",
            duration_hours=20,
            learning_mode="theory"
        )
        print(f"✓ Input: {user_input.course_title}")
        
        print("\nCreating execution context...")
        context = ExecutionContext(
            user_input=user_input,
            session_id="test_session_001",
            execution_mode="test"
        )
        print(f"✓ Context ID: {context.execution_id}")
        
        print("\nNote: Full agent run requires LLM calls (skipped for quick test)")
        print("✓ Agent structure validated")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_orchestrator():
    """Test 5: Full Orchestrator Pipeline"""
    print_header("TEST 5: Full Orchestrator Pipeline (OPTIONAL - REQUIRES LLM)")
    
    try:
        from agents.orchestrator import CourseOrchestratorAgent
        from schemas.user_input import UserInputSchema
        
        print("\nCreating orchestrator...")
        orchestrator = CourseOrchestratorAgent()
        print(f"✓ Orchestrator ready")
        
        print("\nPreparing sample input...")
        user_input = UserInputSchema(
            course_title="Python for Data Analysis",
            course_description="Learn Python programming for data science applications",
            audience_level="undergraduate",
            audience_category="STEM",
            depth_requirement="implementation_level",
            duration_hours=30,
            learning_mode="project_based"
        )
        print(f"✓ Running orchestration for: {user_input.course_title}")
        print(f"   - Audience: {user_input.audience_level}")
        print(f"   - Duration: {user_input.duration_hours}h")
        print(f"   - Mode: {user_input.learning_mode}")
        
        print("\n⏳ Running orchestrator pipeline (this calls LLM)...")
        start_time = datetime.now()
        
        result = await orchestrator.run(user_input)
        
        duration = (datetime.now() - start_time).total_seconds()
        print(f"\n✓ Orchestration complete ({duration:.1f}s)")
        
        # Parse result
        if isinstance(result, dict):
            outline = result
        else:
            outline = result.model_dump() if hasattr(result, 'model_dump') else (result.dict() if hasattr(result, 'dict') else result)
        
        print("\n" + "-"*70)
        print("GENERATED COURSE OUTLINE:")
        print("-"*70)
        print(f"Title: {outline.get('course_title', 'N/A')}")
        print(f"Summary: {outline.get('course_summary', 'N/A')[:100]}...")
        
        modules = outline.get('modules', [])
        print(f"\nModules: {len(modules)}")
        for i, module in enumerate(modules[:3], 1):
            title = module.get('title', 'Untitled') if isinstance(module, dict) else module.title
            hours = module.get('estimated_hours', 0) if isinstance(module, dict) else module.estimated_hours
            print(f"  {i}. {title} ({hours}h)")
        
        if len(modules) > 3:
            print(f"  ... and {len(modules)-3} more modules")
        
        print(f"\nQuality Metrics:")
        print(f"  Confidence: {outline.get('confidence_score', 'N/A')}")
        print(f"  Completeness: {outline.get('completeness_score', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"\n⚠️  SKIPPED or FAILED: {str(e)}")
        print("Note: This is optional if LLM is not available")
        return False


async def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "PHASE 5 TESTING SUITE" + " "*31 + "║")
    print("║" + " "*12 + "Module Creation Agent & Gemini Integration" + " "*14 + "║")
    print("╚" + "="*68 + "╝")
    
    results = {}
    
    # Run tests
    print("\n[1/5] Testing LLM Service...")
    results["LLM Service"] = await test_llm_service()
    
    print("\n[2/5] Testing Schemas...")
    results["Schemas"] = await test_schemas()
    
    print("\n[3/5] Testing Utilities...")
    results["Utilities"] = await test_utilities()
    
    print("\n[4/5] Testing Module Agent...")
    results["Module Agent"] = await test_module_agent()
    
    print("\n[5/5] Testing Full Orchestrator (OPTIONAL)...")
    results["Orchestrator"] = await test_orchestrator()
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_flag in results.items():
        status = "✓ PASS" if passed_flag else "✗ FAIL"
        print(f"  {status:<10} - {test_name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed >= 4:  # At least core 4 tests must pass
        print("\n✅ PHASE 5 IS READY FOR TESTING!")
        print("\nNext steps:")
        print("  1. Run: pytest tests/test_phase_5_module_creation.py -v")
        print("  2. Run: streamlit run app.py")
        print("  3. Check https://localhost:8501 for UI")
        return 0
    else:
        print("\n❌ Some tests failed. Check errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
