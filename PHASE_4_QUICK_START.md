# Phase 4 Quick Start Guide

## What is Phase 4?

Phase 4 (Web Search Agent) adds **external public knowledge** to your system:

```
Phase 3: Internal Knowledge (vector DB - java.txt, examples)
Phase 4: External Knowledge (web search - Tavily, DuckDuckGo, SerpAPI)
         ↓
     Both available to ModuleCreationAgent for synthesis
```

## Test Phase 4 in 3 Steps

### 1. Run Unit Tests

```bash
cd c:\Users\nisha\Projects\tcs_ai\course_ai_agent

# Run all Phase 4 tests
pytest tests/test_phase_4_web_search.py -v

# Expected: 30 tests pass
```

### 2. Test Manually (Python)

```python
import asyncio
from agents.web_search_agent import WebSearchAgent
from schemas.execution_context import ExecutionContext
from schemas.user_input import (
    UserInputSchema, AudienceLevel, AudienceCategory, 
    LearningMode, DepthRequirement
)

async def test():
    # Create user input
    user_input = UserInputSchema(
        course_title="Python Programming",
        course_description="Learn Python basics",
        audience_level=AudienceLevel.BEGINNER,
        audience_category=AudienceCategory.COLLEGE_STUDENTS,
        learning_mode=LearningMode.HYBRID,
        depth_requirement=DepthRequirement.INTRODUCTORY,
        duration_hours=40,
    )
    
    # Create context
    context = ExecutionContext(user_input=user_input, session_id="test")
    
    # Run web search agent
    agent = WebSearchAgent()
    output = await agent.run(context)
    
    # Print results
    print(f"✅ Web Search Complete")
    print(f"   Confidence: {output.confidence_score}")
    print(f"   Results: {output.result_count}")
    print(f"   Tool: {output.tool_used.value}")
    print(f"\n📚 Summary:\n{output.search_summary[:200]}...")
    print(f"\n🔗 Top Sources:")
    for link in output.source_links[:3]:
        print(f"   - {link.title}")
        print(f"     {link.url}")

# Run it
asyncio.run(test())
```

### 3. Test with Full Orchestrator

```python
import asyncio
from agents.orchestrator import CourseOrchestratorAgent
from schemas.user_input import (
    UserInputSchema, AudienceLevel, AudienceCategory,
    LearningMode, DepthRequirement
)

async def test():
    # Create request
    user_input = UserInputSchema(
        course_title="Full Stack Web Development",
        course_description="Learn web dev",
        audience_level=AudienceLevel.INTERMEDIATE,
        audience_category=AudienceCategory.WORKING_PROFESSIONALS,
        learning_mode=LearningMode.PROJECT_BASED,
        depth_requirement=DepthRequirement.IMPLEMENTATION_LEVEL,
        duration_hours=80,
    )
    
    # Run orchestrator (includes Phase 4)
    orchestrator = CourseOrchestratorAgent()
    outline = await orchestrator.run(user_input, session_id="full_test")
    
    print(f"✅ Orchestrator Complete")
    print(f"   Modules: {len(outline['modules'])}")
    print(f"   Duration: {outline['total_duration_hours']} hours")
    print("\n📋 Modules:")
    for module in outline['modules'][:3]:
        print(f"   - {module['title']}")

asyncio.run(test())
```

## What Happens in Phase 4?

### Query Generation
```
User Input: "Machine Learning for Business"
             Audience: Working Professionals
             Depth: Implementation Level

Generated Queries:
1. "Machine Learning for Business syllabus curriculum"
2. "Machine Learning for Business working_professionals course outline"
3. "Machine Learning for Business learning objectives implementation_level"
```

### Web Search (Multi-Tool)

```
Query 1 → Try Tavily → No auth? → Try DuckDuckGo → Got results? ✅
Query 2 → Try Tavily → Insufficient? → Try DuckDuckGo → Try SerpAPI ✅
Query 3 → Try Tavily → Got results? ✅

Deduplicate URLs
 ↓
All Results
```

### LLM Synthesis

```
Raw Results (10-15 URL snippets)
    ↓
LLM Prompt (antihallu hallucination template)
    ↓
Extracted:
- Key topics
- Recommended modules
- Learning objectives
- Required skills
    ↓
WebSearchAgentOutput (structured, high confidence)
```

### Integration with ModuleCreationAgent

```
ExecutionContext now has:
├─ retrieved_documents (from Phase 3/Retrieval)
├─ web_search_results (from Phase 4/WebSearch) ← NEW
└─ user_input

ModuleCreationAgent uses both when generating outline
```

## Key Classes & Methods

### WebSearchAgent

```python
class WebSearchAgent:
    async def run(context: ExecutionContext) → WebSearchAgentOutput
    # Main entry point
    
    async def _generate_search_queries(user_input) → List[str]
    # Strategic query planning
    
    async def _execute_batch_search(queries) → Tuple[List[SearchResult], dict]
    # Multi-tool search
    
    async def _synthesize_results(...) → WebSearchAgentOutput
    # LLM-powered synthesis
```

### WebSearchToolchain

```python
class WebSearchToolchain:
    def search(query: str, max_results: int = 5) → Tuple[List[SearchResult], str]
    # Try Tavily → DuckDuckGo → SerpAPI
    
    def batch_search(queries: List[str]) → Tuple[List[SearchResult], dict]
    # Search multiple queries
    
    def deduplicate_results(results) → List[SearchResult]
    # Remove duplicate URLs
```

### WebSearchAgentOutput

```python
class WebSearchAgentOutput:
    search_query: str
    search_summary: str  # max 1000 words
    key_topics_found: List[str]
    source_links: List[SourceLink]  # URLs with metadata
    confidence_score: float  # 0.0-1.0
    tool_used: SearchTool  # Tavily/DuckDuckGo/SerpAPI
    execution_time_ms: float
    fallback_used: bool
```

## Fallback Chain

```
Primary (Tavily)
  - High quality, educational focus
  - Requires API key: TAVILY_API_KEY
  - Fastest, most relevant
  
Secondary (DuckDuckGo) ← If Tavily insufficient
  - Free, no auth needed
  - Privacy-focused, reliable
  - duckduckgo_search package required
  
Tertiary (SerpAPI) ← If DuckDuckGo insufficient
  - Structured results
  - Requires API key: SERPAPI_API_KEY
  - Most fallback tries
  
Final ← All exhausted
  - Return low-confidence results
  - Continue to ModuleCreationAgent anyway
```

## Configuration

### Environment Variables

```bash
# Optional - for real web search
export TAVILY_API_KEY="your_tavily_key"
export SERPAPI_API_KEY="your_serpapi_key"

# Not needed for DuckDuckGo (free)
```

### Mock Mode (Default)

All tools work in mock mode without API keys:

```python
# Returns realistic mock responses
# No network calls
# Deterministic for testing
# Perfect for development
```

## Troubleshooting

### "Web search is not finding results"

```python
# Check what's being searched:
from agents.web_search_agent import WebSearchAgent
from schemas.user_input import UserInputSchema, ...

agent = WebSearchAgent()
user_input = UserInputSchema(...)
queries = await agent._generate_search_queries(user_input)
print(queries)
# Adjust user_input values if queries are too generic
```

### "Confidence score is low (< 0.5)"

```python
# Low confidence means:
# - Few results found
# - Low relevance scores from web sources
# - Fallback tools were used

# Still valid! ModuleCreationAgent continues
output.is_usable()  # Check if results are good enough
output.search_notes  # See why confidence is low
```

### "Tool returned no results"

```python
# Non-blocking! System continues:
if context.web_search_results is None:
    # Fall back to internal knowledge only
    # Phase 3 Retrieval + user requirements still available
```

## File Locations

```
Root
├── tools/
│   └── web_search_tools.py          ← Tool wrappers
├── schemas/
│   └── web_search_agent_output.py   ← Output schema
├── agents/
│   ├── web_search_agent.py          ← Main agent
│   └── orchestrator.py              ← Integration (UPDATED)
├── prompts/
│   └── web_search_agent.txt         ← Anti-hallucination template
├── tests/
│   └── test_phase_4_web_search.py   ← 30 tests
└── PHASE_4_COMPLETE.md              ← Full documentation
```

## Next Steps

1. ✅ Run tests: `pytest tests/test_phase_4_web_search.py -v`
2. ✅ Test manually: Use code examples above
3. ✅ Check orchestrator integration: "Full Orchestrator Test"
4. ⏳ Phase 5: ModuleCreationAgent will consume web results
5. ⏳ Phase 6: Validator Agent (fact-checking)

## Success Checklist

- [ ] `pytest tests/test_phase_4_web_search.py` passes (30 tests)
- [ ] Manual Python test runs without errors
- [ ] Orchestrator test includes web search in logs
- [ ] Confidence scores are reasonable (>= 0.5 for good results)
- [ ] Source links are valid URLs
- [ ] No hallucinated URLs in results
- [ ] Fallback chain works (try different tools)

All set? You're ready for Phase 5! 🚀

