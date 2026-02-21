# Phase 4 Visual Reference Guide

## 1. System Architecture (Bird's Eye View)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          User Interface                                 │
│                        (Streamlit/API)                                  │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                     CourseOrchestrator                                   │
│                   (Traffic Controller)                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Step 1: Parse Input    ┌─────────────────────────────┐               │
│          ↓              │ UserInputSchema:            │               │
│  Step 2: Create Context │ - title                     │               │
│          ↓              │ - audience_category         │               │
│  Step 3: Log Start      │ - depth_requirement         │               │
│                         │ - learning_mode             │               │
│                         │ - session_id                │               │
│                         └─────────────────────────────┘               │
│                              │                                        │
│    ┌─────────────────────────┼─────────────────────────┐              │
│    │                         ↓                         │              │
│    │    ┌────────────────────────────────┐            │              │
│    │    │ PHASE 3: RetrievalAgent       │            │              │
│    │    │                                │            │              │
│    │    │ Step 4: Search ChromaDB        │            │              │
│    │    │ (institutional knowledge)      │            │              │
│    │    │                                │            │              │
│    │    │ Output:                        │            │              │
│    │    │ retrieved_documents ────┐      │            │              │
│    │    └────────────────────────────────┘      │      │              │
│    │                                            │      │              │
│    │    ┌────────────────────────────────┐      │      │              │
│    │    │ PHASE 4: WebSearchAgent       │★ NEW  │      │              │
│    │    │                                │      │      │              │
│    │    │ Step 5: Search Web             │      │      │              │
│    │    │ (public knowledge)             │      │      │              │
│    │    │                                │      │      │              │
│    │    │ Output:                        │      │      │              │
│    │    │ web_search_results ────┐      │      ↓      │              │
│    │    └────────────────────────────────┘      │  ExecutionContext  │
│    │                    ↓                      │      │              │
│    └────────────────────────┼──────────────────┘      │              │
│                             ↓                        │              │
│                ┌────────────────────────┐             │              │
│                │PHASE 2: ModuleCreation │             │              │
│                │                        │             │              │
│                │ Step 6: Generate       │★ Enhanced   │              │
│                │ (uses both sources)    │  (has both │              │
│                │                        │   knowledge)              │
│                │ Output:                │             │              │
│                │ CourseOutlineSchema    │             │              │
│                └────────────┬───────────┘             │              │
│                             ↓                        │              │
│                ┌────────────────────────┐             │              │
│                │ Step 7: Validate       │             │              │
│                │ Step 8: Log Complete   │             │              │
│                └────────────────────────┘             │              │
└──────────────────────────────────────────────────────────────────────┘
                             │
                             ↓
┌──────────────────────────────────────────────────────────────────────┐
│                  CourseOutlineSchema (JSON)                         │
│                                                                      │
│  {                                                                  │
│    "course_title": "...",                                          │
│    "modules": [...],                                               │
│    "learning_outcomes": [...],                                     │
│    "total_duration_hours": 60,                                     │
│    "references": [                                                 │
│      {"from": "internal", "url": "..."},  (Phase 3)               │
│      {"from": "external", "url": "..."},  (Phase 4)               │
│    ]                                                               │
│  }                                                                  │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 2. WebSearchAgent Data Flow

```
┌─────────────────────────┐
│   User Input Schema     │
│                         │
│ course_title:           │
│ "Machine Learning"      │
│                         │
│ audience_category:      │
│ "professionals"         │
│                         │
│ depth_requirement:      │
│ "implementation"        │
└────────────┬────────────┘
             │
             ↓
┌─────────────────────────────────────────────────┐
│ Step 1: Generate Queries                        │
│                                                 │
│ Input: course_title + context                   │
│                                                 │
│ Output:                                         │
│ [                                               │
│   "ML syllabus curriculum",                     │
│   "ML professionals course outline",            │
│   "ML implementation learning objectives"       │
│ ]                                               │
└────────────┬────────────────────────────────────┘
             │
             ↓
┌──────────────────────────────────────────────────┐
│ Step 2: Batch Search (WebSearchToolchain)       │
│                                                  │
│ Input: 3 queries                                 │
│                                                  │
│ Execution:                                       │
│ For each query:                                  │
│   Try Tool 1: Tavily                            │
│   If insufficient → Try Tool 2: DuckDuckGo      │
│   If insufficient → Try Tool 3: SerpAPI         │
│                                                  │
│ Output:                                          │
│ {                                                │
│   "query1": [Result, Result, Result, ...],      │
│   "query2": [Result, Result, Result, ...],      │
│   "query3": [Result, Result, Result, ...]       │
│ }                                                │
└────────────┬─────────────────────────────────────┘
             │
             ↓
┌──────────────────────────────────────────────────┐
│ Step 3: Deduplicate Results                      │
│                                                  │
│ Input: All results (possibly with duplicates)    │
│                                                  │
│ Logic: Remove by URL                             │
│                                                  │
│ Output:                                          │
│ [Result(url1), Result(url2), Result(url3), ...]│
│ (no duplicate URLs)                              │
└────────────┬─────────────────────────────────────┘
             │
             ↓
┌────────────────────────────────────────────────────┐
│ Step 4: Format for LLM                             │
│                                                    │
│ Input: Deduplicated results (top 10)               │
│                                                    │
│ Format:                                            │
│ """                                                │
│ SEARCH RESULTS FOR QUERY: "..."                   │
│                                                    │
│ 1. Title: "..."                                   │
│    URL: "https://..."                             │
│    Snippet: "..."                                 │
│                                                    │
│ 2. Title: "..."                                   │
│    ...                                            │
│ """                                                │
│                                                    │
│ Output: Formatted string ready for LLM             │
└────────────┬────────────────────────────────────────┘
             │
             ↓
┌────────────────────────────────────────────────────┐
│ Step 5: LLM Synthesis                              │
│                                                    │
│ Input:                                             │
│ - Prompt template (from prompts/...)              │
│ - Formatted results                                │
│ - User context (course_title, audience, etc)      │
│                                                    │
│ LLM Extracts:                                      │
│ - Key topics                                       │
│ - Recommended modules                              │
│ - Learning objectives                              │
│ - Skill recommendations                            │
│ - Confidence assessment                            │
│                                                    │
│ Output: JSON with structured data                  │
│                                                    │
│ FALLBACK if LLM fails:                             │
│ - Use simple extraction (regex, keywords)          │
│ - Return low confidence score (0.3)                │
└────────────┬────────────────────────────────────────┘
             │
             ↓
┌──────────────────────────────────────────────────┐
│ Step 6: Calculate Confidence & Metrics            │
│                                                  │
│ Confidence Score:                                 │
│ (Based on # results, LLM quality, source reps)   │
│                                                  │
│ High Confidence: 0.85+                            │
│ Usable: 0.3+                                     │
│ Low Confidence: < 0.3                             │
│                                                  │
│ Metrics:                                          │
│ - result_count                                   │
│ - high_quality_result_count                      │
│ - execution_time_ms                              │
│ - tool_used (tavily | duckduckgo | serpapi)     │
│ - fallback_used (bool)                           │
└────────────┬──────────────────────────────────────┘
             │
             ↓
┌──────────────────────────────────────────────────┐
│ WebSearchAgentOutput                              │
│                                                  │
│ {                                                │
│   "search_query": "Machine Learning",            │
│   "search_summary": "Based on ...",              │
│   "key_topics_found": [...],                     │
│   "recommended_modules": [...],                  │
│   "source_links": [...],                         │
│   "learning_objectives_found": [...],            │
│   "skillset_recommendations": [...],             │
│   "confidence_score": 0.87,                      │
│   "result_count": 12,                            │
│   "high_quality_result_count": 8,                │
│   "tool_used": "tavily",                         │
│   "execution_timestamp": "2024-...",             │
│   "execution_time_ms": 1245,                     │
│   "fallback_used": false,                        │
│   "search_notes": "All results from..."          │
│ }                                                │
└──────────────────────────────────────────────────┘
```

---

## 3. Tool Fallback Chain Decision Tree

```
                    Execute Search
                          │
                          ↓
                  ┌───────────────┐
                  │ Try Tavily    │
                  │ (Primary)     │
                  └───────┬───────┘
                          │
              ┌───────────┴────────────┐
              │                        │
         Success?              No/Limited
         (>2 results)              Results
              │                        │
              ↓                        ↓
         Return Results      ┌──────────────────┐
         tool_used="tavily"  │ Try DuckDuckGo   │
         fallback_used=false │ (Secondary)      │
                             └────────┬─────────┘
                                      │
                          ┌───────────┴────────────┐
                          │                        │
                     Success?              No/Limited
                     (>2 results)              Results
                          │                        │
                          ↓                        ↓
                     Return Results      ┌──────────────────┐
                     tool_used="duckduckgo"  │ Try SerpAPI      │
                     fallback_used=true  │ (Tertiary)       │
                                         └────────┬─────────┘
                                                  │
                              ┌───────────────────┴──────────────┐
                              │                                  │
                         Success?                          No Results
                         (any results)                   All Failed
                              │                                  │
                              ↓                                  ↓
                         Return Results          ┌──────────────────────┐
                         tool_used="serpapi"     │ Return Empty Output  │
                         fallback_used=true      │ (Graceful Failure)   │
                                                 │                      │
                                                 │ tool_used="unknown"  │
                                                 │ confidence_score=0.0 │
                                                 │ result_count=0       │
                                                 │ fallback_used=true   │
                                                 │ search_notes=        │
                                                 │  "All tools failed"  │
                                                 └──────────────────────┘
                                                         │
                                                         ↓
                                                  Orchestrator continues
                                                  (non-blocking)
```

---

## 4. ExecutionContext Evolution

```
Stage 1: User Input
┌────────────────────────┐
│ ExecutionContext       │
├────────────────────────┤
│ user_input: {...}      │
│ session_id: "..."      │
│ timestamps: {...}      │
└────────────────────────┘

                    ↓ (Step 4: RetrievalAgent)

Stage 2: After Retrieval
┌────────────────────────────┐
│ ExecutionContext           │
├────────────────────────────┤
│ user_input: {...}          │
│ retrieved_documents: {     │
│   chunks: [...],           │
│   summary: "...",          │
│ }                          │
│ session_id: "..."          │
│ timestamps: {...}          │
└────────────────────────────┘

                    ↓ (Step 5: WebSearchAgent)

Stage 3: After Web Search
┌──────────────────────────────┐
│ ExecutionContext             │
├──────────────────────────────┤
│ user_input: {...}            │
│ retrieved_documents: {...}   │ ← From Phase 3
│ web_search_results: {        │ ← From Phase 4 (NEW)
│   topics: [...],             │
│   links: [...],              │
│   confidence: 0.87,          │
│ }                            │
│ session_id: "..."            │
│ timestamps: {...}            │
└──────────────────────────────┘

                    ↓ (Step 6: ModuleCreationAgent)
                    
                    (Uses BOTH sources)

Stage 4: Final Course Outline
┌──────────────────────────────┐
│ CourseOutlineSchema          │
├──────────────────────────────┤
│ course_title                 │
│ modules: [                   │
│   {                          │
│     title: "...",            │
│     description: "...",      │
│     references_from: [       │
│       {"type": "internal"},  │
│       {"type": "external"},  │
│     ]                        │
│   },                         │
│   ...                        │
│ ]                            │
│ learning_outcomes            │
│ total_duration_hours         │
└──────────────────────────────┘
```

---

## 5. Confidence Score Interpretation

```
Confidence Range: 0.0 → 1.0

1.0 │                                    ← Perfect (rare)
    │
0.9 │  ████████████████ ← HIGH CONFIDENCE
    │  Used for generation
0.8 │
    │  ████████████████
0.7 │  ╱╱╱╱╱╱╱╱╱╱╱╱╱╱ ← THRESHOLD (default)
    │  
0.6 │
    │  
0.5 │  ════════════════ ← MEDIUM
    │  Review before use
0.4 │
    │
0.3 │  ════════════════ ← USABLE THRESHOLD
    │  Fallback available
0.2 │  ▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ← LOW
    │  Should reconsider
0.1 │
    │
0.0 │  ░░░░░░░░░░░░░░ ← NO RESULTS
    │                    (fallback to internal only)
    └─────────────────────────────────

    When confidence_score >= 0.7:
      ✅ is_high_confidence() = True
      ✅ Use results for generation
      ✅ Mark as external reference
    
    When 0.3 <= confidence_score < 0.7:
      ⚠️ is_usable() = True
      ⚠️ Can use, but review first
      ⚠️ Consider confidence in output
    
    When confidence_score < 0.3:
      ❌ is_usable() = False
      ❌ Should not use for generation
      ❌ Revert to internal knowledge only
```

---

## 6. Test Coverage Map

```
Phase 4 Test Suite (30 tests)

TestSearchTools                      ┐
├─ initialization                    │
├─ result_format                     │  Toolchain Tests (8)
├─ deduplication                     │
├─ fallback_chain (CRITICAL)         │
├─ batch_search                      │
├─ singleton_pattern                 │
├─ search_stats                      │
└─ search_history                    ┘

TestWebSearchAgentOutput             ┐
├─ creation                          │
├─ empty_search                      │  Schema Tests (8)
├─ confidence_thresholds             │
├─ source_link_dataclass             │
├─ recommended_module_dataclass      │
├─ to_dict_serialization             │
├─ from_dict_deserialization         │
└─ str_representation                ┘

TestWebSearchAgent                   ┐
├─ initialization                    │
├─ query_generation                  │  Agent Tests (7)
├─ full_pipeline                     │
├─ no_results_handling               │
├─ llm_synthesis                     │
├─ synthesis_with_fallback           │
└─ search_budget                     ┘

TestFailureResilience                ┐
├─ network_error_handling            │  Resilience Tests (5)
├─ llm_service_failure               │
├─ timeout_handling                  │
├─ all_tools_fail                    │
└─ malformed_llm_response            ┘

TestProvenance                       ┐
├─ tool_attribution                  │  Provenance Tests (4)
├─ execution_timing                  │
├─ fallback_tracking                 │
└─ source_link_urls                  ┘

TestPhase4Integration                 Integration Test (1)
└─ end_to_end_pipeline               Full system verification

TOTAL: 30 async tests covering all components
```

---

## 7. Performance Profile

```
Execution Timeline

WebSearchAgent.run() Timeline:
│
├─ Generate Queries: ~50ms
│  └─ Parse input, create 3 queries
│
├─ Batch Search: ~1000-1500ms
│  ├─ Query 1 (Tavily): ~300-500ms
│  ├─ Query 2 (Tavily): ~300-500ms
│  └─ Query 3 (Tavily): ~300-500ms
│  (If fallback: +500-1000ms per query)
│
├─ Deduplicate: ~10ms
│  └─ Compare URLs, remove duplicates
│
├─ Format Results: ~20ms
│  └─ Convert to LLM input format
│
├─ LLM Synthesis: ~500-3000ms
│  ├─ Send to LLM service
│  ├─ Parse response: ~50ms
│  └─ Fallback if needed: ~100ms
│
├─ Calculate Metrics: ~10ms
│  └─ Set confidence, timestamps
│
└─ Return: ~5ms
   └─ Serialize output

TOTAL: ~1500-5000ms (1.5-5 seconds)
           Typical: ~2 seconds

Orchestrator Full Pipeline:

Input
  ↓ 50ms (normalize)
Retrieval: ~270ms
  ↓
WebSearch: ~2000ms ← NEW (Phase 4)
  ↓
ModuleCreation: ~5000-30000ms (depends on LLM)
  ↓
Output: ~10ms

TOTAL: ~7-32 seconds per request
Typical: ~15 seconds (acceptable for web app)
```

---

## 8. Integration Decision Matrix

```
                              Orchestrator Scenario
                    
                    ┌─────────────────────────────────────┐
                    │ Web Search Available                │
                    │ (Internet connection, API keys)     │
                    ├─────────────────────────────────────┤
                    │                                     │
                    │  Use:                               │
                    │  ✅ Retrieval + WebSearch          │
                    │  ✅ Both sources in context         │
                    │  ✅ ModuleCreation enhanced         │
                    │  ✅ Higher quality outline          │
                    │                                     │
                    └─────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
         ┌──────────▼──────────┐        ┌──────────▼──────────┐
         │ Web Search          │        │ Web Search          │
         │ SUCCEEDS            │        │ FAILS               │
         │                     │        │                     │
         │ ✅ Confidence: 0.7+ │        │ ⚠️ Graceful failure │
         │ ✅ Multiple results │        │ ✅ Continue anyway  │
         │ ✅ External refs    │        │ ✅ Use internal only│
         │ ✅ Enhanced module  │        │ ✅ Outline still OK │
         │                     │        │ ⚠️ Lower confidence│
         └─────────────────────┘        └────────────────────┘
                    │                               │
                    └───────────────┬───────────────┘
                                    │
                            ┌───────▼────────┐
                            │                │
                    ┌───────▼────────┐      │
                    │ ModuleCreation │◄─────┘
                    │ (BOTH SOURCES) │
                    │                │
                    │ Uses:          │
                    │ - Internal     │
                    │ - External     │
                    │                │
                    │ Output:        │
                    │ - Rich outline │
                    │ - Both refs    │
                    │ - Cross-ref    │
                    └────────────────┘
                            │
                            │
                    ┌───────▼────────┐
                    │ Course Outline │
                    │ (FINAL)        │
                    └────────────────┘
```

---

## 9. Error Handling Flow

```
WebSearchAgent.run() → ExecutionPath

START
  │
  ├─→ Generate Queries
  │   ├─ ✅ Success → Continue
  │   └─ ❌ Error → Return empty_search()
  │
  ├─→ Try Batch Search
  │   ├─ ✅ Success → Continue with results
  │   └─ ❌ Network error → Log, continue
  │
  ├─→ Search with Toolchain
  │   ├─ ✅ Results found → Continue
  │   ├─ ⚠️ Fallback tried → Log, continue
  │   └─ ❌ All fail → Empty results
  │
  ├─→ Deduplicate
  │   ├─ ✅ Success → Continue
  │   └─ ❌ Error → Return all (undedup)
  │
  ├─→ Format for LLM
  │   ├─ ✅ Success → Continue
  │   └─ ❌ Error → Skip to fallback
  │
  ├─→ LLM Synthesis
  │   ├─ ✅ Valid JSON → Parse, return
  │   ├─ ⚠️ Invalid JSON → Try fallback
  │   └─ ❌ API error → Use simple extraction
  │
  ├─→ Simple Extraction (fallback)
  │   ├─ ✅ Keywords found → Return with low confidence
  │   └─ ❌ No extraction → Empty output
  │
  ├─→ Calculate Confidence
  │   ├─ ✅ Set score based on results
  │   └─ ⚠️ Adjust for fallback
  │
  └─→ Return WebSearchAgentOutput
      ├─ confidence_score ∈ [0.0, 1.0]
      ├─ result_count ∈ [0, N]
      ├─ fallback_used ∈ [True, False]
      └─ search_notes describes path taken

END → Orchestrator continues (non-blocking)
```

---

## 10. Configuration & Customization

```
WebSearchAgent Configuration

class WebSearchAgent:
    def __init__(
        self,
        search_budget: int = 3,           # Max queries per request
        min_results: int = 2,             # Min acceptable results
        confidence_threshold: float = 0.7, # High confidence cutoff
        timeout_ms: int = 5000,           # Search timeout
        use_mock: bool = False            # Mock mode for testing
    ):
```

WebSearchToolchain Configuration

"""
Environment Variables:
- TAVILY_API_KEY: Tavily API key (if not set, uses mock)
- SERPAPI_API_KEY: SerpAPI key (if not set, skipped)
- WEB_SEARCH_MOCK: Set to "true" to use mock mode

Code Configuration:
- min_results_threshold: 2 (acceptable minimum)
- max_results_per_query: 5 (default)
- search_timeout_ms: 5000 (per tool)
"""

LLM Synthesis Configuration

"""
Prompt Template: prompts/web_search_agent.txt
- Customizable template variables
- Anti-hallucination constraints
- Example scenarios

LLM Service: via llm_service module
- Primary: Configured LLM (Claude, GPT, etc.)
- Fallback: Simple keyword extraction
- Timeout: 30 seconds
"""

Orchestrator Configuration

"""
Phase 4 Step (Step 5):
- Enabled: True (default)
- Blocking: False (non-blocking)
- Skip on error: True (continue if fails)

ExecutionContext:
- Stores: retrieved_documents (Phase 3)
- Stores: web_search_results (Phase 4)
- Available to: ModuleCreationAgent
"""
```

---

## 11. Quick Decision Guide

**When to Use Web Search (Phase 4)?**

```
✅ USE if:
  - Need current/public information
  - Validating internal knowledge
  - Discovering new resources
  - Comprehensive curriculum required
  - Public knowledge expected

❌ SKIP if:
  - Network unavailable
  - API quotas exceeded
  - Private/confidential content only
  - Internal knowledge sufficient
  - Speed critical
```

**Confidence Score Interpretation:**

```
score >= 0.7    → ✅ HIGH: Use for generation
0.3-0.7         → ⚠️ MEDIUM: Review first
score < 0.3     → ❌ LOW: Use internal only
score == 0.0    → ❌ NONE: No external results
```

**Tool Selection Logic:**

```
Tavily (Primary)
├─ Requires: API key + internet
├─ Benefits: High quality results
├─ Fallback: To DuckDuckGo
└─ When: If configured & available

DuckDuckGo (Secondary)
├─ Requires: Internet
├─ Benefits: Always available, free
├─ Fallback: To SerpAPI
└─ When: Tavily fails/unavailable

SerpAPI (Tertiary)
├─ Requires: API key + internet
├─ Benefits: Structured results
├─ Fallback: Return empty
└─ When: DuckDuckGo fails

None Available
└─ Return: Empty output (non-blocking)
```

---

*Reference Guide Complete - All Visual Diagrams for Phase 4*

