# Phase 4 Architecture & Design Decisions

## System Architecture After Phase 4

```
┌────────────────────────────────────────────────────────────────┐
│                      User Interface (Streamlit)               │
│                                                                │
│  Form Input: Title, Audience, Depth, Mode, Duration           │
└──────────────────────────┬─────────────────────────────────────┘
                           │
                           ↓
┌────────────────────────────────────────────────────────────────┐
│              Orchestrator (Traffic Controller)                 │
│                                                                │
│  Step 1: Normalize input → UserInputSchema                    │
│  Step 2: Build ExecutionContext                               │
│  Step 3: Log execution start                                  │
│                                                                │
│    ┌───────────────────────────────────────────────────┐      │
│    │  PHASE 3: RetrievalAgent (Private Memory)        │      │
│    │                                                   │      │
│    │  Step 4: Search ChromaDB for institutional        │      │
│    │          knowledge (java.txt chunks)             │      │
│    │                                                   │      │
│    │  Output: retrieved_documents (vector DB results) │      │
│    │  Non-blocking: continues if search fails         │      │
│    └──────────────────┬────────────────────────────────┘      │
│                       │                                        │
│         ┌─────────────┼─────────────┐                         │
│         │ (internal)  │             │ (external)              │
│         ↓             │             ↓                         │
│  ExecutionContext     │    ┌───────────────────────────────┐  │
│  ├─ user_input        │    │ PHASE 4: WebSearchAgent       │  │
│  ├─ retrieved_docs ───┤    │ (Public Knowledge)            │  │
│  └─ web_search_results├────┤                               │  │
│                       │    │ Step 5: Search web for        │  │
│                       │    │         public curriculum     │  │
│                       │    │                               │  │
│                       │    │ Queries: 3 strategic          │  │
│                       │    │ Tools: Tavily→DuckDuckGo→...  │  │
│                       │    │                               │  │
│                       │    │ Output: web_search_results    │  │
│                       │    │ Non-blocking: continues if... │  │
│                       │    └───────────┬───────────────────┘  │
│                       │                │                      │
│         ┌─────────────┴────────────────┘                      │
│         │                                                     │
│         ↓                                                     │
│    ┌──────────────────────────────────────┐                 │
│    │ PHASE 2: ModuleCreationAgent         │                 │
│    │                                      │                 │
│    │ Step 6: Generate course outline      │                 │
│    │         using:                       │                 │
│    │         - User requirements          │                 │
│    │         - Internal knowledge         │                 │
│    │         - Public knowledge           │                 │
│    │         - LLM synthesis              │                 │
│    │                                      │                 │
│    │ Output: CourseOutlineSchema          │                 │
│    └──────────────┬───────────────────────┘                 │
│                   │                                         │
│  Step 7: Validate output                                    │
│  Step 8: Log completion                                     │
└───────────────────┼─────────────────────────────────────────┘
                    │
                    ↓
┌────────────────────────────────────────────────────────────────┐
│           Course Outline Schema (JSON)                         │
│                                                                │
│  {                                                             │
│    "course_title": "...",                                      │
│    "modules": [                                                │
│      {"title": "...", "content": "...", ...},                  │
│      {"title": "...", "content": "...", ...},                  │
│    ],                                                          │
│    "total_duration_hours": 60,                                 │
│    "learning_outcomes": [...],                                │
│    "references": [                                             │
│      {"from": "internal", "url": "..."},  (Phase 3)           │
│      {"from": "external", "url": "..."},  (Phase 4)           │
│    ]                                                           │
│  }                                                             │
└────────────────────────────────────────────────────────────────┘
```

## Orchestrator Flow (Sequence Diagram)

```
User
  │
  ├─→ Orchestrator.run(user_input, session_id)
  │
  │   Step 1: Normalize UserInputSchema
  │   Step 2: Build ExecutionContext
  │   Step 3: Log start
  │
  ├─→ Phase 3: RetrievalAgent.run(context)
  │   ├─→ Check vector store (ChromaDB)
  │   ├─→ Generate search queries
  │   ├─→ Search & deduplicate
  │   ├─→ Return RetrievalAgentOutput
  │   └─→ context.retrieved_documents = output.to_dict()
  │   (Non-blocking: if fails, context.retrieved_documents = None)
  │
  ├─→ Phase 4: WebSearchAgent.run(context)  ← NEW
  │   ├─→ Generate web search queries
  │   ├─→ Try Tavily search
  │   ├─→ If insufficient, try DuckDuckGo
  │   ├─→ If insufficient, try SerpAPI
  │   ├─→ Synthesize with LLM
  │   ├─→ Return WebSearchAgentOutput
  │   └─→ context.web_search_results = output.to_dict()
  │   (Non-blocking: if fails, context.web_search_results = None)
  │
  ├─→ Phase 2: ModuleCreationAgent.run(context)
  │   ├─→ Access context.user_input
  │   ├─→ Access context.retrieved_documents (if available)
  │   ├─→ Access context.web_search_results (if available)
  │   ├─→ Generate course outline
  │   └─→ Return CourseOutlineSchema
  │
  ├─→ Validate output
  │
  └─→ Return CourseOutlineSchema.dict()
        (JSON suitable for Streamlit frontend)
```

## Component Interactions

### Phase 3 + Phase 4 Parallelism

```
    ExecutionContext
           │
      ┌────┴────┐
      │          │
      ↓          ↓
  RetrievalAgent WebSearchAgent  (Could run in parallel!)
      │          │
      ├─→ Institutional Memory
      │   └─→ ChromaDB (java.txt)
      │       └─→ Chunks + embeddings
      │
      └─→ Public Knowledge
          └─→ Web Search
              ├─→ Tavily
              ├─→ DuckDuckGo
              └─→ SerpAPI

Combine in ExecutionContext:
  context.retrieved_documents ← Phase 3
  context.web_search_results  ← Phase 4
  
Both available to ModuleCreationAgent
```

### Tool Selection Strategy (WebSearch)

```
Query: "Machine Learning for Professionals"

┌─────────────────────────────────────┐
│ Try Tool 1: Tavily                  │
├─────────────────────────────────────┤
│ Results: 15 high-quality findings   │
│ Status: ✅ Sufficient!              │
│ Use: YES                            │
└─────────────────────────────────────┘
      tool_used = "tavily"
      fallback_used = False


If Tavily had failed:
┌─────────────────────────────────────┐
│ Try Tool 2: DuckDuckGo              │
├─────────────────────────────────────┤
│ Results: 8 reasonable findings      │
│ Status: ✅ Sufficient!              │
│ Use: YES                            │
└─────────────────────────────────────┘
      tool_used = "duckduckgo"
      fallback_used = True


If Both failed:
┌─────────────────────────────────────┐
│ Try Tool 3: SerpAPI                 │
├─────────────────────────────────────┤
│ Results: 3 findings                 │
│ Status: ⚠️ Low confidence            │
│ Use: YES (better than nothing)      │
└─────────────────────────────────────┘
      tool_used = "serpapi"
      fallback_used = True
      confidence_score = 0.5


If All tried and exhausted:
┌─────────────────────────────────────┐
│ Return: WebSearchAgentOutput.empty()│
├─────────────────────────────────────┤
│ Results: None                       │
│ Status: ❌ No meaningful results    │
│ Use: NO                             │
│ Continue: Yes! (non-blocking)       │
└─────────────────────────────────────┘
      tool_used = "unknown"
      fallback_used = True
      confidence_score = 0.0
```

## Data Flow: ExecutionContext

```
ExecutionContext (Single source of truth)
│
├─ user_input: UserInputSchema
│  ├─ course_title: "Machine Learning"
│  ├─ audience_category: "working_professionals"
│  ├─ depth_requirement: "implementation_level"
│  └─ ...
│
├─ retrieved_documents: Optional[dict]  (Phase 3)
│  └─ From RetrievalAgent.to_dict()
│     ├─ retrieved_chunks: [...]
│     ├─ knowledge_summary: "..."
│     ├─ retrieval_confidence: 0.8
│     └─ ...
│
├─ web_search_results: Optional[dict]  (Phase 4) ← NEW
│  └─ From WebSearchAgentOutput.to_dict()
│     ├─ search_summary: "..."
│     ├─ key_topics_found: [...]
│     ├─ source_links: [...]
│     ├─ confidence_score: 0.7
│     └─ ...
│
└─ execution_id, session_id, timestamps...

Available to ModuleCreationAgent:
- What does user want?
- What do we know internally?
- What's available publicly?
- How confident are we in each?
```

## LLM Prompt Flow (Phase 4)

```
User Input
  │
  ├─ Course Title: "Machine Learning"
  ├─ Audience: "working_professionals"
  ├─ Depth: "implementation_level"
  └─ Mode: "project_based"
  
  ↓
  
Query Planning:
  1. "Machine Learning syllabus curriculum"
  2. "Machine Learning working_professionals course outline"
  3. "Machine Learning learning objectives implementation_level"
  
  ↓
  
Web Search (Toolchain):
  Tools: Tavily → DuckDuckGo → SerpAPI
  Results: 15+ URLs + snippets
  
  ↓
  
Format Results:
  1. Stanford ML Course - syllabus
     URL: https://...
     Snippet: "Covers supervised, unsupervised..."
     Score: 0.95
  
  2. Coursera ML Specialization
     URL: https://...
     Snippet: "Professional learning path..."
     Score: 0.92
  
  [More...]
  
  ↓
  
LLM Synthesis Prompt:
  ┌─────────────────────────────────┐
  │ Prompt Template                 │
  │ (from prompts/...)              │
  │                                 │
  │ Role: Educational curator       │
  │ Task: Extract from results      │
  │ Constraints:                    │
  │ - No hallucination              │
  │ - Only from provided results    │
  │ - Structured JSON output        │
  │ - Cite all sources              │
  │                                 │
  │ Input: Formatted results        │
  │ Output: JSON schema             │
  └─────────────────────────────────┘
  
  ↓
  
LLM (Claude/GPT/Ollama):
  - Reads prompt
  - Extracts key topics
  - Identifies recommended modules
  - Extracts learning objectives
  - Recommends skills
  - Rates confidence
  
  ↓
  
Structured Output:
  {
    "search_summary": "ML resources emphasize...",
    "key_topics_found": ["supervised learning", ...],
    "recommended_modules": [...],
    "learning_objectives_found": ["Students will learn...", ...],
    "skillset_recommendations": ["Python", ...],
    "confidence_notes": "Based on 5+ authoritative sources"
  }
  
  ↓
  
WebSearchAgentOutput:
  ├─ search_summary
  ├─ key_topics_found
  ├─ recommended_modules
  ├─ source_links (with URLs)
  ├─ confidence_score: 0.85
  ├─ tool_used: "tavily"
  └─ execution_time_ms: 234
```

## Design Decisions & Rationale

### 1. **Multi-Tool Fallback**

**Decision:** Try Tavily → DuckDuckGo → SerpAPI

**Why:**
- Single tool dependency risk
- Tavily: Best quality (requires API key)
- DuckDuckGo: Always available (no auth)
- SerpAPI: Structured fallback
- Never completely fails

### 2. **Non-Blocking Integration**

**Decision:** Web search failures don't crash orchestrator

**Code:**
```python
try:
    web_search_output = await agent.run()
    context.web_search_results = output.to_dict()
except:
    context.web_search_results = None  # Continue
```

**Why:**
- Network unreliability
- API quotas can be exceeded
- LLM synthesis can fail
- System must be resilient
- Internal knowledge alone is sufficient

### 3. **LLM-Powered Synthesis**

**Decision:** Use LLM for structured output (not simple extraction)

**Why:**
- Raw snippets aren't structured enough
- LLM can extract meaning from results
- Organized output for ModuleCreationAgent
- Still anti-hallucination via prompt template

### 4. **ExecutionContext as Accumulator**

**Decision:** Pass context through pipeline, accumulate results

**Why:**
- Single source of truth
- ModuleCreationAgent has visibility
- Easy to add Phase 5, 6, 7 agents
- Session-level persistence friendly

### 5. **Provenance Tracking**

**Decision:** Record tool used, URLs, timestamps, confidence

**Why:**
- Trust and transparency
- Debugging tool performance
- Audit trails
- User explainability (future)
- Identify hallucinations (future validator)

## Comparison: Phase 3 vs Phase 4

```
                    Phase 3 (Retrieval)     Phase 4 (WebSearch)
─────────────────────────────────────────────────────────────
Data Source        Internal (ChromaDB)     External (Public)
                   Vector DB with          Web APIs
                   user curricula

Query Type         Vector similarity       Web search queries
                   (embedding-based)       (keyword/semantic)

Results            Chunks from DB          URL + snippets
                   with metadata           from web

Confidence         Based on similarity     Based on source
                   scores                  authority + quantity

Speed              Fast (local)            Slower (network)

Cost               Free (computed once)    API costs (if using Tavily)

Updates            Manual (process          Live (always current)
                   new documents)

Trust              High (your data)        Variable (public sources)

Use Case           Institutional memory    Curriculum research,
                   (what YOU know)         validation (what's public)
```

## Flow Comparison: Single Agent vs. Two Agents

### Before (Phase 3 only - RetrievalAgent only):
```
User → Retrieval → ModuleCreation → Outline
                   (limited by internal knowledge only)
```

### After (Phase 3 + Phase 4 - Both agents):
```
User → Retrieval ──┐
       (internal)  ├─→ Module Creation → Outline
       Web Search ─┘   (uses both sources)
       (external)
```

**Benefit:** Richer, better-grounded course outlines

## Future Extensibility (Phase 5+)

The architecture now supports adding agents without breaking existing code:

```
User
  │
  ├─→ RetrievalAgent     (Phase 3, private memory)
  ├─→ WebSearchAgent     (Phase 4, public memory)
  ├─→ ???Agent           (Phase 5, validation?)
  ├─→ ???Agent           (Phase 6, query?
  └─→ ModuleCreationAgent
```

Each agent:
- ✅ Receives ExecutionContext
- ✅ Returns structured output
- ✅ Updates context
- ✅ Non-blocking (failures don't crash)
- ✅ Can be swapped/improved independently

## Performance Considerations

```
Phase 3 (Retrieval):
  Time: ~270ms (5 queries × 50ms each)
  Complexity: O(queries × documents)
  Network: Local (no latency)

Phase 4 (WebSearch):
  Time: ~500-2000ms (depends on tools, network, LLM)
  Complexity: O(queries × tools tried)
  Network: External (3-5 HTTP requests)

Total Orchestrator:
  Baseline: ~770ms-2700ms
  (Could parallelize Phases 3&4 in future)

ModuleCreationAgent:
  Time: ~5-30s (depends on LLM)
  Network: External (LLM API call)

Total Request:
  Range: ~6-33 seconds
  (Acceptable for web app)
```

## Security & Risk

### Phase 4 Risks

1. **Malicious URLs in search results**
   - Mitigation: Show URLs to user, don't auto-execute
   - Validation: Only return HTTPS URLs

2. **API quota exceeded**
   - Mitigation: Fallback chain, graceful degradation
   - Monitoring: Track tool usage stats

3. **LLM hallucination in synthesis**
   - Mitigation: Prompt constraints, fact-based only
   - Validation: Future phase 6 validator

4. **PII in web snippets**
   - Mitigation: Anonymize snippets, brief text
   - User responsibility: Review before publishing

### Mitigations Built In

- ✅ Anti-hallucination prompt template
- ✅ Non-blocking (failures don't cascade)
- ✅ Provenance tracking (audit trail)
- ✅ Confidence scoring (users know reliability)
- ✅ Fallback chain (never crashes)
- ✅ Rate limiting (search budget limited)

