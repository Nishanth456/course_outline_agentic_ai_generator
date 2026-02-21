# PHASE 4 — Web Search Agent (External Knowledge Layer)

**Status:** ✅ COMPLETE

**Outcome:** Your system can intelligently fetch public curriculum information from the web with clean fallback logic, structured summaries, and full provenance tracking without polluting core agent logic.

## Overview

Phase 4 adds a **Web Search Agent** that operates in parallel with the Retrieval Agent:

```
User Input
    ↓
┌─────────────────────────────────┐
│      Orchestrator               │
├─────────────────────────────────┤
│ Step 4: RetrievalAgent          │ ← Phase 3 (internal knowledge)
│ Step 5: WebSearchAgent          │ ← Phase 4 (external/public knowledge)  
│ Step 6: ModuleCreationAgent     │ ← Synthesizes both
└─────────────────────────────────┘
    ↓
Course Outline (grounded in internal + external knowledge)
```

## Architecture Overview

### Components

```
tools/web_search_tools.py
├── TavilySearchTool (primary)
├── DuckDuckGoSearchTool (secondary)
├── SerpAPISearchTool (tertiary fallback)
└── WebSearchToolchain (orchestrator)

schemas/web_search_agent_output.py
├── WebSearchAgentOutput (main output)
├── SearchTool (enum)
├── RecommendedModule
├── SourceLink
└── SearchResult

agents/web_search_agent.py
└── WebSearchAgent
    ├── Query generation
    ├── Batch search
    ├── LLM synthesis
    └── Structured output

prompts/web_search_agent.txt
└── Prompt template (prevents hallucination)

agents/orchestrator.py (UPDATED)
└── Step 5: WebSearchAgent call (non-blocking)
```

## Key Features

### 1. Multi-Tool Fallback Chain 🔄

**Fallback order:**
```
Try Tavily (primary - high quality)
  ↓ (if insufficient)
Try DuckDuckGo (secondary - no API key needed)
  ↓ (if insufficient)
Try SerpAPI (tertiary - structured results)
  ↓ (if insufficient)
Return empty results gracefully
```

**Benefits:**
- Never completely fails
- Graceful degradation
- No single point of failure
- Each tool tracked for observability

### 2. Intelligent Query Planning 🎯

Based on user context, generates 3 strategic queries:

```python
Query 1: "{course} syllabus curriculum"
Query 2: "{course} {audience} course outline"
Query 3: "{course} learning objectives {depth}"
```

**Adapts to:**
- Course title
- Audience category
- Depth requirement
- Learning mode

### 3. LLM-Powered Synthesis 🧠

Uses LLM (via `llm_service`) to:

```
Raw Search Results
    ↓
Format + Score
    ↓
LLM Synthesis
   ├─ Extract key topics
   ├─ Identify learning objectives
   ├─ Recommend modules
   ├─ Extract required skills
   └─ Calculate confidence
    ↓
Structured WebSearchAgentOutput
```

**Prevents hallucination via prompt template** (`prompts/web_search_agent.txt`)

### 4. Clean Provenance Tracking 📍

Every result is traceable:

```
{
  "search_query": "...",
  "source_links": [
    {
      "url": "https://...",
      "title": "...",
      "source_type": "external",
      "relevance_score": 0.92,
      "accessed_at": "2026-02-21T19:00:00"
    }
  ],
  "tool_used": "tavily",
  "fallback_used": false,
  "execution_time_ms": 234,
  "search_notes": "..."
}
```

## Implementation Details

### Step 4.1: Role Boundary ✅

**WebSearchAgent Responsibilities:**
- ✅ Find publicly available educational information
- ✅ Summarize findings
- ✅ Provide URLs & confidence scores
- ✅ Track fallback usage

**WebSearchAgent Non-Responsibilities:**
- ❌ No module generation
- ❌ No validation/scoring
- ❌ No direct UI access
- ❌ No internal database access

### Step 4.2: Tool Strategy ✅

**Tool Wrappers:** `tools/web_search_tools.py`

```python
class TavilySearchTool:
    """Primary: paid API, high quality educational focus"""

class DuckDuckGoSearchTool:
    """Secondary: free, no auth needed, privacy-focused"""

class SerpAPISearchTool:
    """Tertiary: structured results, requires API key"""

class WebSearchToolchain:
    """Master orchestrator with fallback logic"""
```

**Mock Implementations:**
- For testing without real API keys
- Realistic responses for common queries
- Deterministic behavior

### Step 4.3: Query Planning ✅

**Algorithm:** `agents/web_search_agent.py::_generate_search_queries()`

```python
async def _generate_search_queries(user_input):
    # Query 1: Syllabus/curriculum
    f"{course_title} syllabus curriculum"
    
    # Query 2: Contextual outline
    f"{course_title} {audience_category} course outline"
    
    # Query 3: Learning depth
    f"{course_title} learning objectives {depth_requirement}"
    
    return queries[:self.search_budget]  # Max 3
```

**Benefits:**
- Contextual, not generic
- Focused on curriculum
- Respects user context
- Controlled budget (max 3 queries)

### Step 4.4: Output Schema ✅

**File:** `schemas/web_search_agent_output.py`

```python
@dataclass
class WebSearchAgentOutput:
    # Core
    search_query: str
    search_summary: str  # max 1000 words
    
    # Structured Data
    key_topics_found: List[str]
    recommended_modules: List[RecommendedModule]
    source_links: List[SourceLink]
    learning_objectives_found: List[str]
    skillset_recommendations: List[str]
    
    # Quality Metrics
    confidence_score: float  # 0.0 - 1.0
    result_count: int
    high_quality_result_count: int
    
    # Provenance
    tool_used: SearchTool  # tavily, duckduckgo, etc.
    execution_timestamp: str
    execution_time_ms: Optional[float]
    fallback_used: bool
    search_notes: str
```

**Guarantees:**
- ✅ No raw HTML
- ✅ No confusing source mixing
- ✅ Every result traceable
- ✅ Confidence scores present

### Step 4.5: LLM Service Integration ✅

**Interface:** Uses existing `services/llm_service.py`

```python
# Web Search Agent uses standardized LLM interface
llm_service = get_llm_service()
response = await llm_service.generate(
    prompt=synthesis_prompt,
    system_prompt="You are an educational curator..."
)
```

**Benefits:**
- Vendor-agnostic
- Swappable providers
- Mock-friendly for testing
- Centralized configuration

### Step 4.6: Prompt Template ✅

**File:** `prompts/web_search_agent.txt`

**Features:**
- Anti-hallucination constraints
- Fact-based extraction only
- Structured JSON output
- Example scenarios
- Error handling guidelines

**Sample enforcement:**
```
⚠️  CRITICAL:
- Only summarize what appears in provided search results
- Do NOT add information not in the results
- Do NOT hallucinate sources
- Do NOT mention any internal curriculum files
- Keep summary under 1000 words
```

### Step 4.7: Orchestrator Integration ✅

**File:** `agents/orchestrator.py` (UPDATED)

**New Flow:**

```python
async def run(self, user_input, session_id):
    context = ExecutionContext(...)
    
    # Step 4: Retrieval (internal knowledge)
    try:
        retrieval_output = await self.retrieval_agent.run(context)
        context.retrieved_documents = retrieval_output.to_dict()
    except:
        context.retrieved_documents = None  # Non-blocking
    
    # Step 5: Web Search (external knowledge) ← NEW
    try:
        web_search_output = await self.web_search_agent.run(context)
        context.web_search_results = web_search_output.to_dict()
    except:
        context.web_search_results = None  # Non-blocking
    
    # Step 6: Module Creation (uses both)
    outline = await self.module_agent.run(context)
    
    return outline.dict()
```

**Rules:**
- ✅ Non-blocking (failure doesn't stop pipeline)
- ✅ Both internal + external knowledge available to ModuleCreationAgent
- ✅ Orchestrator remains thin (just routing)
- ✅ No orchestrator logic in agents

### Step 4.8: Provenance & Explainability ✅

**What's Tracked:**

```python
output = WebSearchAgentOutput(
    # Tool Attribution
    tool_used=SearchTool.TAVILY,
    fallback_used=False,
    
    # Source Links
    source_links=[
        SourceLink(
            url="https://...",
            title="...",
            relevance_score=0.92,
            accessed_at="2026-02-21T19:00:00"
        )
    ],
    
    # Execution Trace
    execution_timestamp="2026-02-21T19:00:00",
    execution_time_ms=234,
    search_notes="Based on 5 reliable sources..."
)
```

**Benefits:**
- Every insight traceable
- Tool performance visible
- Fallback usage documented
- Timestamps for audit trails

### Step 4.9: Failure & Degradation ✅

**Failure Scenarios:**

```
Scenario 1: API Quota Exceeded
  → Try next tool in chain
  → If all exhausted, return low-confidence results

Scenario 2: Zero Results
  → Return empty_search()
  → Confidence = 0.0
  → Pipeline continues to generation

Scenario 3: LLM Synthesis Fails
  → Fallback to simple extraction
  → No hallucination
  → Still returns valid output

Scenario 4: Network Timeout
  → Caught, logged
  → Non-blocking
  → ModuleCreationAgent proceeds anyway
```

**System Behavior:**

```python
# In orchestrator
try:
    web_search_output = await self.web_search_agent.run(context)
    context.web_search_results = web_search_output.to_dict()
except Exception as e:
    self.logger.warning(f"Web search failed (non-blocking): {e}")
    context.web_search_results = None  # Continue anyway

# ModuleCreationAgent checks availability
if context.web_search_results:
    use_web_knowledge()
else:
    use_only_internal_knowledge()
```

### Step 4.10: Test Suite ✅

**File:** `tests/test_phase_4_web_search.py`

**30 Comprehensive Tests:**

```
TestSearchTools (8 tests)
├── Tool initialization
├── Result format
├── Deduplication
├── Batch search
└── History tracking

TestWebSearchAgentOutput (8 tests)
├── Schema creation
├── Serialization
├── Confidence scoring
└── Provenance fields

TestWebSearchAgent (7 tests)
├── Query generation
├── Full pipeline
├── Error handling
└── Synthesis

TestFailureResilience (5 tests)
├── LLM failures
├── Network errors
└── Timeouts

TestProvenance (4 tests)
├── Tool attribution
├── Timestamp tracking
├── URL validity
└── Fallback documentation

TestPhase4Integration (1 test)
└── Full end-to-end pipeline
```

**Exit Criteria (All Met):**
- ✅ Web search works independently
- ✅ Outputs are structured & summarized
- ✅ Provenance is clean
- ✅ No agent coupling introduced
- ✅ All tests pass

## Usage Examples

### Basic Search

```python
from agents.web_search_agent import WebSearchAgent
from schemas.execution_context import ExecutionContext
from schemas.user_input import UserInputSchema, AudienceLevel, AudienceCategory, LearningMode, DepthRequirement

# Create user input
user_input = UserInputSchema(
    course_title="Machine Learning Fundamentals",
    course_description="Learn ML concepts",
    audience_level=AudienceLevel.INTERMEDIATE,
    audience_category=AudienceCategory.WORKING_PROFESSIONALS,
    learning_mode=LearningMode.PRACTICAL_HANDS_ON,
    depth_requirement=DepthRequirement.IMPLEMENTATION_LEVEL,
    duration_hours=60,
)

# Create context
context = ExecutionContext(user_input=user_input, session_id="test")

# Run agent
agent = WebSearchAgent()
output = await agent.run(context)

# Access results
print(f"Confidence: {output.confidence_score}")
print(f"Topics: {output.key_topics_found}")
print(f"Tool used: {output.tool_used.value}")
for link in output.source_links:
    print(f"  - {link.title}: {link.url}")
```

### With Orchestrator

```python
# Just use the orchestrator normally
# Web search happens automatically in Step 5

orchestrator = CourseOrchestratorAgent()
outline = await orchestrator.run(
    user_input=user_input,
    session_id="my_session"
)
# ModuleCreationAgent now has access to:
# - context.retrieved_documents (from RetrievalAgent)
# - context.web_search_results (from WebSearchAgent)
```

### Manual Tool Chain

```python
from tools.web_search_tools import get_web_search_toolchain

toolchain = get_web_search_toolchain()

# Single search
results, tool = toolchain.search("machine learning course")
for result in results:
    print(f"{result.title} ({result.source}, score={result.relevance_score})")

# Batch search
queries = ["ML curriculum", "deep learning course", "neural networks"]
all_results, stats = toolchain.batch_search(queries)

# Deduplication
unique = toolchain.deduplicate_results(all_results)

# Stats
print(toolchain.get_search_stats())
```

## Files Created/Modified

### Created Files

1. **`tools/web_search_tools.py`** (450 lines)
   - TavilySearchTool
   - DuckDuckGoSearchTool
   - SerpAPISearchTool
   - WebSearchToolchain

2. **`schemas/web_search_agent_output.py`** (270 lines)
   - WebSearchAgentOutput
   - SearchTool (enum)
   - RecommendedModule
   - SourceLink

3. **`agents/web_search_agent.py`** (420 lines)
   - WebSearchAgent
   - Query generation
   - LLM synthesis
   - Fallback handling

4. **`prompts/web_search_agent.txt`** (180 lines)
   - Anti-hallucination constraints
   - Output format spec
   - Example scenarios

5. **`tests/test_phase_4_web_search.py`** (600 lines)
   - 30 comprehensive tests
   - Fallback logic tests
   - Provenance tests
   - Integration tests

### Modified Files

1. **`agents/orchestrator.py`**
   - Added WebSearchAgent import
   - Added web_search_agent initialization
   - Added Step 5 (WebSearchAgent call)
   - Renumbered subsequent steps

## System State After Phase 4

Your architecture now has clear separation:

```
Input User Request
    ↓
┌──────────────────────────────────────────────┐
│           Orchestrator                       │
├──────────────────────────────────────────────┤
│ Step 4: RetrievalAgent                       │
│         └─> Institutional memory (vector DB) │
│                                              │
│ Step 5: WebSearchAgent                       │
│         └─> Public knowledge (web)           │
│                                              │
│ Step 6: ModuleCreationAgent                  │
│         └─> Synthesis (local LLM)            │
└──────────────────────────────────────────────┘
    ↓
Course Outline (grounded in private + public knowledge)
```

**Key Achievements:**
- ✅ Institutional memory (Phase 3) + Public knowledge (Phase 4)
- ✅ Multi-tool fallback with observability
- ✅ Anti-hallucination constraints
- ✅ Complete provenance tracking
- ✅ Non-blocking integration
- ✅ 30 comprehensive tests
- ✅ Clean agent boundaries

## Next Steps

**Phase 5 (Future):** ModuleCreationAgent Enhancement
- Use both `context.retrieved_documents` and `context.web_search_results`
- Intelligently blend internal + external knowledge
- Cross-reference and validate

**Phase 6 (Future):** Validator Agent
- Quality scoring
- Fact-checking against sources
- Retry logic with feedback loop

**Phase 7 (Future):** Query Agent
- Follow-up interactions
- Clarifications
- Refinements

## Testing

Run Phase 4 tests:

```bash
# Run all Phase 4 tests
pytest tests/test_phase_4_web_search.py -v

# Run specific test class
pytest tests/test_phase_4_web_search.py::TestSearchTools -v

# Run with coverage
pytest tests/test_phase_4_web_search.py --cov=agents,tools,schemas --cov-report=html

# Run asyncio tests
pytest tests/test_phase_4_web_search.py -v -m asyncio
```

## References

- **Architecture:** See PHASE_3_ARCHITECTURE.md for context
- **Tool Wrappers:** `tools/web_search_tools.py`
- **Agent Logic:** `agents/web_search_agent.py`
- **Output Schema:** `schemas/web_search_agent_output.py`
- **Prompts:** `prompts/web_search_agent.txt`
- **Tests:** `tests/test_phase_4_web_search.py`
- **Orchestrator:** `agents/orchestrator.py`

