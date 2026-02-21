"""
Main README for the Course AI Agent project.
"""

# Course AI Agent

📚 AI-powered course outline generator using agentic LLM architecture.

**Status:** Phase 0 Skeleton Complete | Planning Phase

---

## What is This?

A system that generates comprehensive, constraint-respecting course outlines by:

1. **Accepting educator input** (title, description, audience level, depth, duration, optional PDF)
2. **Coordinating multiple AI agents** (Retrieval, Web Search, Module Creation, Validator, Query)
3. **Synthesizing intelligent outlines** aligned to Bloom's taxonomy and backward design principles
4. **Validating quality** with rubric-based scoring and automated feedback loops
5. **Enabling refinement** through interactive follow-ups and targeted regeneration

---

## Architecture (High-Level)

```
Frontend (Streamlit)
       ↓
Orchestrator Agent (coordinator)
       ├─→ Retrieval Agent (ChromaDB) - private knowledge
       ├─→ Web Search Agent (Tavily / DuckDuckGo) - public knowledge
       ├─→ Module Creation Agent - synthesis
       ├─→ Validator Agent - quality gate
       └─→ Query Agent - interactive explanations
       ↓
Frontend Results & Editable Outline
```

---

## Quick Start

### Prerequisites

- Python 3.10+
- Streamlit
- LangChain
- ChromaDB
- OpenAI API key (or alternative LLM)

### Setup

```bash
cd course_ai_agent
pip install -r requirements.txt

# Run tests
pytest tests/

# Run app
streamlit run app.py
```

---

## Project Structure

```
course_ai_agent/
├── app.py                      # Streamlit entry point
├── agents/
│   ├── base.py                # Agent contracts & base classes
│   ├── orchestrator.py         # Main coordinator
│   ├── web_search_agent.py     # Web search (Tavily, DuckDuckGo, SerpAPI)
│   ├── retrieval_agent.py      # RAG (ChromaDB)
│   ├── module_creation_agent.py # Core synthesis engine
│   ├── validator_agent.py      # Quality scoring & feedback
│   └── query_agent.py          # Interactive explanations
├── schemas/
│   ├── user_input.py           # UserInputSchema
│   ├── course_outline.py       # CourseOutlineSchema
│   └── agent_outputs.py        # Per-agent output contracts
├── tools/
│   ├── web_tools.py            # Web search tool wrappers
│   └── pdf_loader.py           # PDF extraction
├── vectorstore/
│   ├── chroma_client.py        # ChromaDB connector
│   └── embeddings.py           # Embedding provider
├── utils/
│   ├── session.py              # Session management
│   ├── scoring.py              # Validator rubric logic
│   └── logging.py              # Observability
├── prompts/
│   └── orchestrator.txt        # Prompt templates
├── tests/                      # Comprehensive test suite (by phase)
├── data/
│   ├── sample_curricula/       # Synthetic test docs
│   └── sample_user_uploads/    # Ephemeral session test files
├── docs/
│   ├── PHASED_IMPLEMENTATION_PLAN.md  # This document
│   ├── architecture.md         # Architecture details
│   └── API_SPECS.md            # API contracts
└── README.md                   # This file
```

---

## Phased Implementation (9 Phases)

We implement incrementally, adding one capability per phase. Each phase is testable and deployable independently.

| Phase | Goal |Duration | Status |
|-------|------|---------|--------|
| 0 | Project skeleton & contracts | 1-2d | ✅ Complete |
| 1 | Streamlit UI + session mgmt | 3-4d | 🟢 Ready |
| 2 | Orchestrator (single-pass) | 4-5d | 🟢 Ready |
| 3 | Retrieval Agent + ChromaDB | 5-6d | 🟢 Ready |
| 4 | Web Search Agent | 4-5d | 🟢 Ready |
| 5 | Module Creation Agent | 8-10d | 🟢 Ready |
| 6 | Validator Agent (agentic loop) | 6-7d | 🟢 Ready |
| 7 | Query Agent (interactive) | 4-5d | 🟢 Ready |
| 8 | UX polish & exports | 5-6d | 🟢 Ready |
| 9 | Observability & metrics | 4-5d | 🟢 Ready |

See [PHASED_IMPLEMENTATION_PLAN.md](docs/PHASED_IMPLEMENTATION_PLAN.md) for detailed breakdown.

---

## Key Contracts & Schemas

### Input: UserInputSchema

```python
{
  "course_title": "Introduction to Machine Learning",
  "course_description": "...",
  "audience_level": "undergraduate",
  "audience_category": "cs_major",
  "learning_mode": "hybrid",
  "depth_requirement": "implementation",
  "duration_hours": 40,
  "pdf_path": "/tmp/session_123.pdf",  # optional
  "custom_constraints": "..."
}
```

### Output: CourseOutlineSchema

```python
{
  "course_title": "...",
  "course_summary": "...",
  "audience_level": "undergraduate",
  "modules": [
    {
      "module_id": "M_1",
      "title": "Foundations",
      "learning_objectives": [
        {
          "statement": "Explain supervised vs unsupervised learning",
          "bloom_level": "understand",
          "assessment_method": "quiz"
        }
      ],
      "lessons": [...]
    }
  ],
  "citations_and_provenance": [...]
}
```

Full schemas: [schemas/](schemas/)

---

## Testing

Tests are organized by phase:

```bash
# Phase 0 - Schema validation
pytest tests/test_schemas.py

# Phase 1 - UI + Session
pytest tests/test_phase_1_ui.py

# Phase 5 - Module Creation Agent
pytest tests/test_phase_5_module_creation.py

# Phase 6 - Validator Agent (agentic behavior)
pytest tests/test_phase_6_validator.py

# Run all
pytest tests/
```

---

## Configuration

Set environment variables:

```bash
# LLM
export OPENAI_API_KEY="sk-..."
export LLM_MODEL="gpt-4-turbo"

# Web Search
export TAVILY_API_KEY="tvly-..."
export DUCKDUCKGO_ENABLED=true

# ChromaDB
export CHROMA_DB_PATH="./chroma_data"

# Session
export SESSION_TTL_MINUTES=30
export TEMP_DIR="/tmp/course_ai_sessions"

# Validator
export VALIDATOR_THRESHOLD=75
export MAX_REGENERATION_ATTEMPTS=3
```

---

## API Usage (PHASE 2+)

### Generate Course Outline

```bash
curl -X POST http://localhost:8000/api/outline \
  -H "Content-Type: application/json" \
  -d '{
    "course_title": "Intro to ML",
    "course_description": "...",
    "audience_level": "undergraduate",
    "learning_mode": "hybrid",
    "depth_requirement": "implementation",
    "duration_hours": 40
  }'
```

Response:
```json
{
  "session_id": "uuid",
  "status": "accepted",
  "outline": { ... CourseOutlineSchema ... },
  "validator_score": 88,
  "regeneration_attempts": 1
}
```

---

## Data Privacy & Security

✅ **Session PDFs:** Ephemeral (stored in temp, auto-deleted after session)
✅ **Persistent Storage:** Only curriculum metadata + embeddings (no PII)
✅ **Logging:** Pseudonymized (session IDs, no names)
✅ **Exports:** Consent captured, revision history maintained

---

## Contributing

1. Check [PHASED_IMPLEMENTATION_PLAN.md](docs/PHASED_IMPLEMENTATION_PLAN.md) for current phase
2. Implement phase contracts (see schemas/)
3. Write tests for your phase
4. Run tests: `pytest tests/test_phase_X.py`
5. Submit PR

---

## Roadmap

### Near-term (Post-Phase-9)
- Human-in-the-loop review workflow
- LMS integration (Moodle, Canvas)
- Student capability adaptivity
- Analytics dashboard

### Future
- Multi-language support
- Real-time collaborative editing
- AI-powered assessment rubric generation

---

## Support

- **Issues?** See `tests/` for expected behavior
- **Questions?** Check [PHASED_IMPLEMENTATION_PLAN.md](docs/PHASED_IMPLEMENTATION_PLAN.md)
- **Design Docs?** See `docs/` folder

---

**Built with:** Streamlit, LangChain, ChromaDB, LLMs (OpenAI/Anthropic)

**License:** [TBD]

**Status:** Alpha (Phase 0 complete, phases 1-9 in planning)
