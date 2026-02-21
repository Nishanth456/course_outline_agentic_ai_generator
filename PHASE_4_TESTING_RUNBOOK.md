# Phase 4 Testing Runbook

## Quick Start: Run All Tests in 2 Minutes

```bash
# Terminal: Run Phase 4 test suite
cd c:\Users\nisha\Projects\tcs_ai\course_ai_agent
pytest tests/test_phase_4_web_search.py -v

# Expected Output:
# ===== test session starts =====
# tests/test_phase_4_web_search.py::TestSearchTools::test_search_tools_initialization PASSED
# tests/test_phase_4_web_search.py::TestSearchTools::test_search_result_format PASSED
# ... (28 more tests)
# ===== 30 passed in 15.43s =====
```

## Test Categories

### Category 1: Search Tools (8 tests)

**Purpose:** Verify SearchResult format, tool initialization, fallback chain

```
test_search_tools_initialization
├─ Verify TavilySearchTool initializes
├─ Verify DuckDuckGoSearchTool initializes
├─ Verify SerpAPISearchTool initializes
└─ Verify WebSearchToolchain initializes

test_search_result_format
├─ Create SearchResult with title, url
├─ Check dataclass fields exist
├─ Verify relevance_score defaults to 0.8
└─ Confirm source attribute exists

test_toolchain_deduplication
├─ Create 10 results, 4 duplicates
├─ Call toolchain.deduplicate_results()
├─ Verify returns 6 unique (by URL)
└─ Check first occurrence kept

test_toolchain_fallback_chain
├─ Mock all tools to fail
├─ Call toolchain.search()
├─ Verify tries Tavily first
├─ Verify tries DuckDuckGo second
├─ Verify tries SerpAPI third
└─ Verify returns empty list when all fail

[4 more tests: batch search, singleton pattern, search stats, history]
```

**Run individually:**
```bash
pytest tests/test_phase_4_web_search.py::TestSearchTools -v
```

### Category 2: Output Schema (8 tests)

**Purpose:** Validate WebSearchAgentOutput structure, serialization, confidence

```
test_web_search_output_creation
├─ Create empty WebSearchAgentOutput
├─ Set summary, confidence_score
├─ Verify all fields initialized
└─ Check defaults

test_empty_search_output
├─ Call WebSearchAgentOutput.empty_search()
├─ Verify confidence_score = 0.0
├─ Verify result_count = 0
├─ Verify is_usable() returns False

test_confidence_thresholds
├─ Create output with confidence 0.85
├─ Check is_high_confidence() → True
├─ Create output with confidence 0.45
├─ Check is_high_confidence() → False

test_source_link_dataclass
├─ Create SourceLink with URL, title
├─ Set source_type = "institution"
├─ Verify relevance_score attribute
└─ Check accessed_at timestamp

test_recommended_module_dataclass
├─ Create RecommendedModule
├─ Set title, description, topics
├─ Verify source_urls list exists
└─ Check estimated_hours

test_to_dict_serialization
├─ Create WebSearchAgentOutput
├─ Call output.to_dict()
├─ Verify returns dict (JSON-serializable)
├─ Check all fields present

test_from_dict_deserialization
├─ Create dict representation
├─ Call WebSearchAgentOutput.from_dict()
├─ Verify object recreated
├─ Check field values match

test_output_str_representation
├─ Create WebSearchAgentOutput
├─ Call str(output)
├─ Verify readable format
└─ Check confidence visible
```

**Run individually:**
```bash
pytest tests/test_phase_4_web_search.py::TestWebSearchAgentOutput -v
```

### Category 3: Web Search Agent (7 tests)

**Purpose:** Verify agent logic, query generation, LLM synthesis

```
test_agent_initialization
├─ Create WebSearchAgent()
├─ Verify toolchain exists
├─ Check reset_agent() works
└─ Confirm singleton pattern

test_search_query_generation
├─ Call _generate_search_queries()
├─ Verify returns 3 queries
├─ Check queries are contextual
└─ Confirm uses audience_category + depth

test_agent_full_pipeline
├─ Create ExecutionContext
├─ Call agent.run(context)
├─ Verify returns WebSearchAgentOutput
├─ Check execution_time_ms > 0

test_agent_with_no_results
├─ Call agent with query: "xyz_nonexistent_course_123"
├─ Verify handles gracefully
├─ Check returns empty_search()
└─ Confirm soft failure (no exception)

test_llm_synthesis
├─ Create mock results
├─ Call _synthesize_results()
├─ Verify returns structured output
└─ Check summary + topics populated

test_synthesis_with_fallback
├─ Mock LLM to fail
├─ Call _synthesize_results()
├─ Verify falls back to _simple_result_extraction()
├─ Ensure still returns valid output
└─ Check low confidence_score (0.3)

test_agent_search_budget
├─ Create agent with search_budget = 1
├─ Call agent.run()
├─ Verify only 1 query executed
└─ Confirm multiple queries if budget > 1
```

**Run individually:**
```bash
pytest tests/test_phase_4_web_search.py::TestWebSearchAgent -v
```

### Category 4: Failure Resilience (5 tests)

**Purpose:** Verify agent handles errors gracefully, doesn't crash orchestrator

```
test_network_error_handling
├─ Mock search to raise RequestError
├─ Call agent.run()
├─ Verify doesn't raise (catches exception)
├─ Check returns empty_search() or fallback
└─ Confirm orchestrator can continue

test_llm_service_failure
├─ Mock llm_service to raise exception
├─ Call _synthesize_results()
├─ Verify falls back to simple extraction
├─ Check output still valid
└─ Verify confidence_score low (0.3)

test_timeout_handling
├─ Mock search to timeout (5s)
├─ Set timeout threshold
├─ Call agent.run()
├─ Verify catches timeout exception
└─ Check returns empty or next tool

test_all_tools_fail
├─ Mock Tavily, DuckDuckGo, SerpAPI all fail
├─ Call agent.run()
├─ Verify tries all three
├─ Check returns empty_search()
└─ Confirm no unhandled exception

test_malformed_llm_response
├─ Mock LLM to return invalid JSON
├─ Call _parse_synthesized_output()
├─ Verify graceful degradation
├─ Check falls back to simple extraction
└─ Confirm returns valid output
```

**Run individually:**
```bash
pytest tests/test_phase_4_web_search.py::TestFailureResilience -v
```

### Category 5: Provenance Tracking (4 tests)

**Purpose:** Verify attribution, timestamps, source tracking

```
test_tool_attribution
├─ Execute search that uses Tavily
├─ Check output.tool_used = "tavily"
├─ Execute search that uses DuckDuckGo
├─ Check output.tool_used = "duckduckgo"
└─ Execute search that uses SerpAPI
   └─ Check output.tool_used = "serpapi"

test_execution_timing
├─ Record start time
├─ Call agent.run()
├─ Record end time
├─ Verify output.execution_time_ms in expected range
└─ Check timing >= 50ms (network latency)

test_fallback_tracking
├─ Mock primary tool to fail
├─ Call agent.run()
├─ Check output.fallback_used = True
└─ Verify tool_used = fallback tool

test_source_link_urls
├─ Run agent.run()
├─ Get output.source_links
├─ Verify each has valid URL (https://)
├─ Check no empty URLs
└─ Confirm titles present
```

**Run individually:**
```bash
pytest tests/test_phase_4_web_search.py::TestProvenance -v
```

### Category 6: Full Integration (1 test)

**Purpose:** Verify entire phase with realistic input

```
test_phase_4_end_to_end
├─ Create realistic UserInput:
│  ├─ course_title: "Machine Learning Fundamentals"
│  ├─ audience_category: "working_professionals"
│  ├─ depth_requirement: "overview_level"
│  └─ learning_mode: "self_paced"
├─ Create ExecutionContext
├─ Call RetrievalAgent.run() (Phase 3)
├─ Call WebSearchAgent.run() (Phase 4) ← New
├─ Verify context.retrieved_documents populated
├─ Verify context.web_search_results populated
├─ Call ModuleCreationAgent.run()
├─ Verify CourseOutlineSchema returned
├─ Check outline has:
│  ├─ module_list (from all sources)
│  ├─ learning_objectives (merged)
│  └─ references (both internal + external)
└─ Confirm total_duration_hours > 0
```

**Run individually:**
```bash
pytest tests/test_phase_4_web_search.py::TestPhase4Integration::test_phase_4_end_to_end -v
```

## Manual Testing Guide

### Test 1: Verify Basic Search Tool

**Goal:** Confirm search tool initializes and returns structured results

```python
# File: test_manual_phase4.py

import asyncio
from tools.web_search_tools import WebSearchToolchain, SearchResult

def test_search_toolchain():
    """Verify toolchain returns valid SearchResult objects"""
    
    toolchain = WebSearchToolchain()
    print(f"✅ Toolchain initialized")
    
    # Search for common course
    results, tool = toolchain.search("Python programming course", max_results=3)
    
    print(f"📊 Search Results:")
    print(f"  Tool used: {tool}")
    print(f"  Results found: {len(results)}")
    
    for i, result in enumerate(results, 1):
        print(f"\n  [{i}] {result.title}")
        print(f"      URL: {result.url}")
        print(f"      Snippet: {result.snippet[:80]}...")
        print(f"      Relevance: {result.relevance_score}")
        
        # Validate structure
        assert hasattr(result, 'title'), "Missing title"
        assert hasattr(result, 'url'), "Missing url"
        assert hasattr(result, 'snippet'), "Missing snippet"
        assert isinstance(result.relevance_score, float), "relevance_score not float"
        assert 0.0 <= result.relevance_score <= 1.0, "relevance_score out of range"
    
    print(f"\n✅ All results have correct structure")
    print(f"✅ Relevance scores valid")
    
    # Test deduplication
    results_dup = results + results
    unique = toolchain.deduplicate_results(results_dup)
    print(f"\n📊 Deduplication:")
    print(f"  Input: {len(results_dup)} (with duplicates)")
    print(f"  Output: {len(unique)} (unique)")
    assert len(unique) == len(results), "Deduplication failed"
    print(f"✅ Deduplication works correctly")

if __name__ == "__main__":
    test_search_toolchain()
```

**Run:**
```bash
python test_manual_phase4.py
```

**Expected Output:**
```
✅ Toolchain initialized
📊 Search Results:
  Tool used: tavily
  Results found: 3

  [1] Python Programming Course - Beginner to Advanced
      URL: https://...
      Snippet: "Learn Python from basics to advanced...
      Relevance: 0.95

  [2] Python Fundamentals Course
      URL: https://...
      Snippet: "Master Python for data science...
      Relevance: 0.87

  [3] Python Programming Tutorial
      URL: https://...
      Snippet: "Complete guide to Python...
      Relevance: 0.85

✅ All results have correct structure
✅ Relevance scores valid

📊 Deduplication:
  Input: 6 (with duplicates)
  Output: 3 (unique)
✅ Deduplication works correctly
```

### Test 2: Verify WebSearchAgent

**Goal:** Test agent query generation and full pipeline

```python
# File: test_manual_agent.py

import asyncio
from agents.web_search_agent import WebSearchAgent
from schemas.execution_context import ExecutionContext
from schemas.user_input import UserInputSchema

async def test_web_search_agent():
    """Test agent query generation and search"""
    
    agent = WebSearchAgent()
    print(f"✅ Agent initialized")
    
    # Create test input
    user_input = UserInputSchema(
        course_title="Machine Learning Applications",
        audience_category="working_professionals",
        depth_requirement="implementation_level",
        learning_mode="project_based",
        session_id="test_manual"
    )
    
    context = ExecutionContext(
        user_input=user_input,
        session_id="test_manual"
    )
    
    print(f"\n📝 Input:")
    print(f"  Title: {user_input.course_title}")
    print(f"  Audience: {user_input.audience_category}")
    print(f"  Depth: {user_input.depth_requirement}")
    
    # Generate queries
    queries = await agent._generate_search_queries(user_input.course_title)
    print(f"\n🔍 Generated Queries ({len(queries)}):")
    for i, q in enumerate(queries, 1):
        print(f"  [{i}] {q}")
    
    assert len(queries) == 3, "Expected 3 queries"
    print(f"✅ Query generation works")
    
    # Run full agent
    print(f"\n⚙️ Running full agent pipeline...")
    output = await agent.run(context)
    
    print(f"\n📊 Agent Output:")
    print(f"  Search Summary: {output.search_summary[:100]}...")
    print(f"  Key Topics: {output.key_topics_found}")
    print(f"  Confidence: {output.confidence_score}")
    print(f"  Tool Used: {output.tool_used.value}")
    print(f"  Results Count: {output.result_count}")
    print(f"  Execution Time: {output.execution_time_ms}ms")
    
    # Validate output
    assert output.search_query is not None, "Missing search_query"
    assert output.confidence_score >= 0.0, "Invalid confidence"
    assert output.confidence_score <= 1.0, "Invalid confidence"
    assert output.result_count >= 0, "Invalid result count"
    
    print(f"\n✅ Agent output valid")
    print(f"✅ Confidence score: {output.confidence_score}")
    
    if output.is_high_confidence():
        print(f"✅ Result is HIGH CONFIDENCE")
    else:
        print(f"⚠️ Result is LOW CONFIDENCE")
    
    # Check URLs
    if output.source_links:
        print(f"\n📚 Source Links ({len(output.source_links)}):")
        for link in output.source_links[:3]:
            print(f"  - {link.title}")
            print(f"    {link.url[:60]}...")
    
    # Check recommended modules
    if output.recommended_modules:
        print(f"\n📚 Recommended Modules ({len(output.recommended_modules)}):")
        for mod in output.recommended_modules[:2]:
            print(f"  - {mod.title}")
            print(f"    Description: {mod.description[:60]}...")

if __name__ == "__main__":
    asyncio.run(test_web_search_agent())
```

**Run:**
```bash
python test_manual_agent.py
```

**Expected Output:**
```
✅ Agent initialized

📝 Input:
  Title: Machine Learning Applications
  Audience: working_professionals
  Depth: implementation_level

🔍 Generated Queries (3):
  [1] Machine Learning Applications syllabus curriculum
  [2] Machine Learning Applications working_professionals course outline
  [3] Machine Learning Applications learning objectives implementation_level

✅ Query generation works

⚙️ Running full agent pipeline...

📊 Agent Output:
  Search Summary: Based on public sources, machine learning applications courses typically...
  Key Topics: ['supervised learning', 'neural networks', 'model deployment', ...]
  Confidence: 0.82
  Tool Used: tavily
  Results Count: 12
  Execution Time: 1234ms

✅ Agent output valid
✅ Confidence score: 0.82
✅ Result is HIGH CONFIDENCE

📚 Source Links (12):
  - Stanford CS229: Machine Learning
    https://cs229.stanford.edu/...
  - Coursera ML Specialization
    https://www.coursera.org/...
  - Fast.ai Practical Deep Learning
    https://fast.ai/...

📚 Recommended Modules (5):
  - Supervised Learning Fundamentals
    Description: Classification, regression, and evaluation metrics...
  - Deep Learning & Neural Networks
    Description: Neural network architectures, training techniques...
```

### Test 3: Verify Orchestrator Integration

**Goal:** Test Phase 3 + Phase 4 together

```python
# File: test_orchestrator_phase4.py

import asyncio
from agents.orchestrator import CourseOrchestratorAgent
from schemas.user_input import UserInputSchema

async def test_orchestrator_with_web_search():
    """Test orchestrator with both Retrieval + WebSearch"""
    
    orchestrator = CourseOrchestratorAgent()
    print(f"✅ Orchestrator initialized")
    
    user_input = UserInputSchema(
        course_title="Data Science Fundamentals",
        audience_category="beginners",
        depth_requirement="overview_level",
        learning_mode="blended",
        session_id="test_orch"
    )
    
    print(f"\n📝 Input:")
    print(f"  Title: {user_input.course_title}")
    print(f"  Audience: {user_input.audience_category}")
    
    print(f"\n⚙️ Running orchestrator with Phase 3 + Phase 4...")
    
    outline = await orchestrator.run(user_input, "test_orch")
    
    print(f"\n📊 Orchestrator Output:")
    print(f"  Course Title: {outline.course_title}")
    print(f"  Total Duration: {outline.total_duration_hours}h")
    print(f"  Modules: {len(outline.module_list)}")
    print(f"  Learning Outcomes: {len(outline.learning_outcomes)}")
    
    print(f"\n✅ Orchestrator completed successfully")
    print(f"✅ Both Retrieval + WebSearch executed")
    
    # Check that we have references from both
    internal_refs = [r for r in outline.references if r.get("source") == "internal"]
    external_refs = [r for r in outline.references if r.get("source") == "external"]
    
    print(f"\n📚 References:")
    print(f"  Internal (Phase 3): {len(internal_refs)}")
    print(f"  External (Phase 4): {len(external_refs) }")
    print(f"  Total: {len(outline.references)}")

if __name__ == "__main__":
    asyncio.run(test_orchestrator_with_web_search())
```

**Run:**
```bash
python test_orchestrator_phase4.py
```

## Troubleshooting

### Issue: Tests fail with "API key not found"

**Cause:** Tavily API key not set

**Solution:**
```bash
# Either set environment variable
set TAVILY_API_KEY=your_key_here

# Or tests will use mock implementation (recommended for testing)
# Tests include mock_search() that works without API key
```

### Issue: "test_phase_4_web_search.py not found"

**Cause:** Still in wrong directory

**Solution:**
```bash
# Navigate to project root
cd c:\Users\nisha\Projects\tcs_ai\course_ai_agent

# Verify file exists
dir tests/test_phase_4_web_search.py

# Run from project root
pytest tests/test_phase_4_web_search.py -v
```

### Issue: "ModuleNotFoundError: No module named 'tavily'"

**Cause:** Tavily SDK not installed

**Solution:**
```bash
# Install tavily-python
pip install tavily-python

# For testing, this is optional - mock implementation works
```

### Issue: "duckduckgo_search not installed"

**Cause:** DuckDuckGo package optional

**Solution:**
```bash
# Install optional package
pip install duckduckgo-search

# Or tests will skip DuckDuckGo tests gracefully
```

### Issue: Tests timeout (> 30 seconds)

**Cause:** Network latency or LLM API slow

**Solution:**
```bash
# Run with longer timeout
pytest tests/test_phase_4_web_search.py -v --timeout=60

# Or run specific test (faster)
pytest tests/test_phase_4_web_search.py::TestSearchTools -v
```

## Summary

**All 30 tests validate:**
- ✅ Search tools work correctly
- ✅ Output schema is properly structured
- ✅ Agent generates contextual queries
- ✅ Multi-tool fallback executes correctly
- ✅ LLM synthesis works (with fallback)
- ✅ Failures are handled gracefully
- ✅ Provenance is tracked completely
- ✅ Full orchestrator integration works
- ✅ Non-breaking integration with Phase 3
- ✅ System doesn't crash on errors

**Success Criteria:**
```
pytest tests/test_phase_4_web_search.py -v
===== 30 passed in ~15s =====

pytest tests/ -v  
===== 75 passed in ~60s =====
  (Phase 2: 20, Phase 3: 25, Phase 4: 30)
```

