# PHASE 2: BAREBONES ORCHESTRATOR
## Single-Pass Pipeline Implementation Plan

**Status:** 📋 Planning/Specification  
**Target:** End-to-end LLM-powered outline generation  
**Scope:** 10 precise sub-steps  
**Knowledge Base Integration:** Ready for KB IDs when provided  

---

## 🎯 Phase 2 Goal

Transform the app from **UI-only mock** → **real LLM-powered MVP**

```
Before (Phase 1):          After (Phase 2):
UI → Mock Agent            UI → Real Orchestrator → Real Agent → Real LLM → UI
(template-driven)          (structured, intelligent)
```

---

## 📋 PHASE 2 BREAKDOWN (10 Steps)

### 🔹 STEP 2.1 — Lock the Phase-2 Responsibility Boundary

**Responsibility:** Prevent scope creep by explicitly defining Phase 2 boundaries

**What Phase 2 INCLUDES ✅**
- Orchestrator agent (pass-through traffic controller)
- ModuleCreationAgent (first real LLM agent)
- LLMService integration (no direct LLM imports in agents)
- UI ↔ backend wiring (existing form + real pipeline)
- Single-pass execution (no loops)
- Error handling (LLM timeout, invalid JSON, schema mismatch)

**What Phase 2 EXPLICITLY EXCLUDES ❌**
- WebSearchAgent (Phase 4)
- RetrievalAgent + ChromaDB (Phase 3)
- ValidatorAgent + retry logic (Phase 6)
- Query refinement agent (Phase 7)
- UX editing/regeneration (Phase 8)
- Database persistence (Phase 8+)
- Analytics/observability (Phase 9)

**Critical Constraint**
```python
# Orchestrator must call exactly ONE agent in Phase 2
class CourseOrchestratorAgent:
    async def run(context):
        # Step 1: Validate input
        # Step 2: Build context
        # Step 3: Call ModuleCreationAgent ONLY
        return module_agent.run(context)
        # No validation agent call
        # No web search
        # No retrieval
```

**Exit Criteria for Step 2.1**
- [ ] Document boundaries in code comments
- [ ] Add assertion: `assert len(agents_called) == 1`
- [ ] Reject any phase 3+ feature branches in PR review

**Files Affected**
- `agents/orchestrator.py` - Add docstring with boundaries
- `agents/module_creation_agent.py` - Add docstring with scope

---

### 🔹 STEP 2.2 — Define Orchestrator's Exact Role

**Responsibility:** Make Orchestrator a transparent traffic controller, not a decision maker

**Orchestrator Responsibilities (MUST DO)**
1. Accept `UserInputSchema` + context
2. Build execution context object
3. Call `ModuleCreationAgent.run(context)` once
4. Validate return against `CourseOutlineSchema`
5. Log execution (action, timestamp, result)
6. Return result to caller

**Orchestrator Must NOT Do (FORBIDDEN)**
- Write or modify prompts
- Call LLM directly
- Decide content logic
- Apply business rules
- Filter/transform output
- Retry on failure (Phase 6)
- Score results (Phase 6)

**Method Signature**
```python
class CourseOrchestratorAgent:
    """
    Single-pass orchestrator.
    
    Routes UserInputSchema → ModuleCreationAgent → CourseOutlineSchema
    Does NOT:
    - Validate quality
    - Search web
    - Index PDFs
    - Retry on error
    """
    
    async def run(
        self,
        user_input: Union[UserInputSchema, dict],
        session_id: Optional[str] = None,
        execution_mode: str = "single_pass"
    ) -> CourseOutlineSchema:
        """
        Execute single-pass course generation.
        
        Args:
            user_input: Educator's requirements
            session_id: For logging
            execution_mode: "single_pass" only in Phase 2
            
        Returns:
            CourseOutlineSchema with generated outline
            
        Raises:
            ValueError: If input invalid
            TimeoutError: If LLM times out
        """
        pass
```

**Exit Criteria for Step 2.2**
- [ ] Orchestrator ≤ 50 lines (traffic control, not logic)
- [ ] All business logic moved to ModuleCreationAgent
- [ ] Docstring explicitly lists forbidden operations
- [ ] No LLM imports in orchestrator file

**Files Affected**
- `agents/orchestrator.py` - Rewrite for Phase 2 role

---

### 🔹 STEP 2.3 — Create the Phase-2 Execution Context

**Responsibility:** Standardize what agents receive (without tight coupling)

**ExecutionContext Structure**
```python
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class ExecutionContext:
    """Context passed from Orchestrator to agents."""
    
    # Core input
    user_input: UserInputSchema
    
    # Tracking
    session_id: str
    execution_id: str  # UUID for this run
    
    # Optional enrichment (for future phases)
    uploaded_pdf_text: Optional[str] = None  # Raw text, if PDF provided
    uploaded_pdf_metadata: Optional[Dict] = None
    
    # Execution control
    execution_mode: str = "single_pass"  # Phase 2+
    max_tokens: int = 8000  # Per-agent limit
    
    # Future phases will add:
    # retrieved_documents: List[Document] = None
    # web_search_results: List[SearchResult] = None
    # validator_feedback: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for logging/debugging."""
        return {
            "user_input": self.user_input.dict(),
            "session_id": self.session_id,
            "execution_id": self.execution_id,
            "execution_mode": self.execution_mode,
        }
```

**Context Building Logic (in Orchestrator)**
```python
async def run(self, user_input, session_id=None):
    # Normalize input
    if isinstance(user_input, dict):
        user_input = UserInputSchema(**user_input)
    
    # Build context
    context = ExecutionContext(
        user_input=user_input,
        session_id=session_id or uuid4(),
        execution_id=str(uuid4()),
        execution_mode="single_pass",
        # NO pdf_text yet (Phase 3 adds RAG enrichment)
    )
    
    # Log start
    logger.info(f"Starting execution {context.execution_id}")
    
    # Call agent with context
    outline = await self.module_agent.run(context)
    
    return outline
```

**Why This Structure Matters**

Phase 3 additions (no code changes needed):
```python
# Phase 3: Retrieval agent runs, adds documents
context.retrieved_documents = [doc1, doc2, ...]
agent = ModuleCreationAgentWithRAG()
outline = await agent.run(context)

# Phase 4: Web search runs, adds results
context.web_search_results = [result1, result2, ...]

# Phase 6: Validator runs, gives feedback
context.validator_feedback = {"score": 0.82, "issues": [...]}
```

**Exit Criteria for Step 2.3**
- [ ] ExecutionContext defined in new file `schemas/execution_context.py`
- [ ] Context handles missing PDF gracefully
- [ ] Logging records execution_id
- [ ] Tests verify context immutability
- [ ] All agents accept `context` parameter

**Tests Required**
```python
def test_execution_context_creation():
    """Context builds with valid input."""
    context = ExecutionContext(
        user_input=valid_schema,
        session_id="sess123",
    )
    assert context.execution_id is not None
    assert context.execution_mode == "single_pass"

def test_execution_context_no_pdf():
    """Context handles missing PDF."""
    context = ExecutionContext(
        user_input=valid_schema,
        session_id="sess123",
        uploaded_pdf_text=None,
    )
    assert context.uploaded_pdf_text is None

def test_context_serialization():
    """Context serializes to dict."""
    context = ExecutionContext(
        user_input=valid_schema,
        session_id="sess123",
    )
    d = context.to_dict()
    assert "execution_id" in d
```

**Files Affected**
- `schemas/execution_context.py` - NEW
- `agents/orchestrator.py` - Import & use ExecutionContext

---

### 🔹 STEP 2.4 — Implement ModuleCreationAgent (First Real Intelligence)

**Responsibility:** Generate structured course outlines using real LLM

**Current Status**
- ✅ Mock version exists (`agents/module_creation_agent.py`)
- ✅ Returns valid `CourseOutlineSchema`
- ❌ Uses templates, not LLM

**Phase 2 Rewrite: Replace Mock with Real LLM**

**New Method Signature**
```python
class CoreModuleCreationAgent:
    """Generate course outline using structured prompt + LLM."""
    
    async def run(self, context: ExecutionContext) -> CourseOutlineSchema:
        """
        Generate course outline respecting all constraints.
        
        Args:
            context: ExecutionContext with user_input
            
        Returns:
            CourseOutlineSchema with full outline
            
        Raises:
            ValueError: If LLM response invalid
            TimeoutError: If LLM times out
        """
        # Phase 2 flow:
        # 1. Build prompt
        # 2. Call LLMService
        # 3. Parse output
        # 4. Validate schema
        # 5. Return result
```

**Internal Flow**
```python
async def run(self, context: ExecutionContext) -> CourseOutlineSchema:
    user_input = context.user_input
    
    # Step 1: Build prompt with all constraints
    prompt = self._build_prompt(user_input)
    
    # Step 2: Call LLMService (NOT OpenAI directly)
    llm = get_llm_service()
    response = await llm.generate(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
        max_tokens=context.max_tokens,
    )
    
    # Step 3: Parse JSON output (will fail if invalid)
    outline_dict = json.loads(response.content)
    
    # Step 4: Validate against schema (will fail if mismatch)
    outline = CourseOutlineSchema(**outline_dict)
    
    # Step 5: Return validated result
    return outline
```

**Constraint Respect (More Explicit Than Phase 1)**
```python
def _build_prompt(self, user_input: UserInputSchema) -> str:
    """Build structured prompt respecting all constraints."""
    
    prompt = f"""
    Generate a course outline with these constraints:
    
    📌 COURSE BASICS
    - Title: {user_input.course_title}
    - Duration: {user_input.duration_hours} hours total
    - Description: {user_input.course_description}
    
    👥 AUDIENCE
    - Skill Level: {user_input.audience_level.value}
    - Category: {user_input.audience_category.value}
    - Prerequisites: {self._get_prerequisites(user_input.audience_level)}
    
    📚 CONTENT STRUCTURE
    - Learning Mode: {user_input.learning_mode.value}
    - Depth: {user_input.depth_requirement.value}
    - Bloom Levels: {self._get_bloom_levels(user_input.depth_requirement)}
    
    ⏱️ MODULE BREAKDOWN
    - Number of modules: ceil({user_input.duration_hours} / 5) = {self._calc_module_count(user_input.duration_hours)}
    - Duration per module: {user_input.duration_hours / self._calc_module_count(user_input.duration_hours):.1f} hours
    
    ✅ OUTPUT REQUIREMENTS
    - Format: Valid JSON matching CourseOutlineSchema
    - Modules: MUST have 3-5 learning objectives each
    - Assessments: MUST include quiz, project, exam
    - No markdown, no explanations, JSON only
    
    Custom constraints: {user_input.custom_constraints or 'None'}
    
    GENERATE THE COURSE OUTLINE NOW:
    """
    
    return prompt
```

**Helper Methods**
```python
def _get_prerequisites(self, level: AudienceLevel) -> str:
    """Return prerequisites based on audience level."""
    prereqs = {
        AudienceLevel.BEGINNER: "No prerequisites",
        AudienceLevel.INTERMEDIATE: "Basic familiarity with domain",
        AudienceLevel.ADVANCED: "Strong foundational knowledge",
        AudienceLevel.PRO_EXPERT: "Professional experience",
        AudienceLevel.MIXED_LEVEL: "Adaptation to mixed levels",
    }
    return prereqs.get(level, "None")

def _get_bloom_levels(self, depth: DepthRequirement) -> str:
    """Return applicable Bloom's levels based on depth."""
    levels = {
        DepthRequirement.INTRODUCTORY: "Remember, Understand",
        DepthRequirement.CONCEPTUAL: "Understand, Apply",
        DepthRequirement.IMPLEMENTATION_LEVEL: "Apply, Analyze",
        DepthRequirement.ADVANCED_IMPLEMENTATION: "Analyze, Evaluate",
        DepthRequirement.INDUSTRY_LEVEL: "Evaluate, Create",
        DepthRequirement.RESEARCH_LEVEL: "Create, Synthesize",
        DepthRequirement.PHD_LEVEL: "Synthesize, Innovate",
    }
    return levels.get(depth, "Remember-Create")

def _calc_module_count(self, hours: int) -> int:
    """Calculate module count based on duration."""
    return max(2, min(6, math.ceil(hours / 5)))
```

**Exit Criteria for Step 2.4**
- [ ] _build_prompt() ≤ 100 lines
- [ ] LLM called via `get_llm_service()` only
- [ ] Output validated with `CourseOutlineSchema(**output)`
- [ ] All constraints explicitly in prompt
- [ ] Mock methods removed (keep only LLM path)
- [ ] Tests pass with real LLM (mocked in tests)

**Files Affected**
- `agents/module_creation_agent.py` - Rewrite for Phase 2 (LLM-powered)

---

### 🔹 STEP 2.5 — Use llm_service.py Correctly

**Responsibility:** Enforce clean LLM isolation

**Current State**
- ✅ `services/llm_service.py` created (from earlier changes)
- ✅ Supports OpenAI, Anthropic, Ollama, etc.
- ❌ Not yet used in agents

**Phase 2 Integration Rule**

```python
# ✅ CORRECT (Phase 2)
from services import get_llm_service

llm = get_llm_service()
response = await llm.generate(prompt, system_prompt="...")

# ❌ WRONG (not allowed in Phase 2)
import openai
response = await openai.ChatCompletion.acreate(...)

# ❌ WRONG (not allowed in Phase 2)
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
```

**In ModuleCreationAgent**
```python
from services import get_llm_service

class CoreModuleCreationAgent:
    async def run(self, context: ExecutionContext):
        # Get LLM service (respect env config)
        llm = get_llm_service()
        
        # Call generate (never import SDK directly)
        response = await llm.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            max_tokens=context.max_tokens,
        )
        
        # Response is LLMResponse (standardized)
        print(f"Model used: {response.model}")
        print(f"Tokens used: {response.tokens_used}")
        
        return parse_outline(response.content)
```

**Configuration (via Environment)**
```bash
# Production: Real OpenAI
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
LLM_API_KEY=sk-...

# Development: Local Ollama
LLM_PROVIDER=ollama
LLM_MODEL=llama2
LLM_API_BASE=http://localhost:11434

# Testing: Mock (defined later in Phase 2)
LLM_PROVIDER=mock
```

**Why This Matters**
- You can change providers by updating `.env` only
- Agents don't need to know about OpenAI/Anthropic/etc.
- Testing is isolated (mock provider)
- Switching to cheaper LLM (Groq) takes 2 minutes
- Cost optimization without refactoring

**Exit Criteria for Step 2.5**
- [ ] Zero LLM SDK imports in `agents/`
- [ ] All LLM calls use `get_llm_service()`
- [ ] Environment config tested
- [ ] Supports at least 2 providers (OpenAI + Anthropic or Ollama)
- [ ] Provider can be swapped without code changes

**Tests Required**
```python
@pytest.mark.asyncio
async def test_llm_service_via_orchestrator():
    """Orchestrator uses LLM service, not SDK."""
    
    # Set up OpenAI mock
    mock_llm = MockLLMService()
    set_llm_service(mock_llm)
    
    orchestrator = CourseOrchestratorAgent()
    context = ExecutionContext(user_input=valid_schema, session_id="s1")
    
    outline = await orchestrator.run(context)
    
    # Verify LLM was called via service
    assert mock_llm.generate_called == True
    assert outline is not None

@pytest.mark.asyncio
async def test_different_provider():
    """Can swap provider via environment."""
    
    # Set up Anthropic mock
    mock_llm = MockAnthropicLLMService()
    set_llm_service(mock_llm)
    
    orchestrator = CourseOrchestratorAgent()
    context = ExecutionContext(user_input=valid_schema, session_id="s1")
    
    outline = await orchestrator.run(context)
    
    # Works exactly the same
    assert outline is not None
```

**Files Affected**
- `agents/module_creation_agent.py` - Import from services, not SDK
- `agents/orchestrator.py` - Same pattern

---

### 🔹 STEP 2.6 — Prompt Contract for Module Creation

**Responsibility:** Define prompt structure that generates valid, parseable output

**Prompt Strategy**

```python
SYSTEM_PROMPT = """You are an expert curriculum designer.
Your task: Generate a structured course outline in JSON format.

Rules:
1. Output MUST be valid JSON (parseable by Python json.loads)
2. NO markdown, NO formatting, NO explanations
3. Match the provided schema exactly
4. Respect all duration and depth constraints
5. Generate realistic, educationally sound content
6. Use Bloom's taxonomy levels appropriately

Output format: JSON object with course_title, modules[], etc.
"""

USER_PROMPT_TEMPLATE = """
Generate a course outline for:
- Title: {title}
- Duration: {hours} hours
- Audience: {audience_level}, {audience_category}
- Learning Mode: {learning_mode}
- Depth: {depth_requirement}
- Description: {description}

Module count: {module_count} modules
Duration per module: {hours_per_module:.1f} hours

Bloom levels to use: {bloom_levels}

Output as JSON matching this structure:
{{
  "course_title": "string",
  "course_summary": "string",
  "modules": [
    {{
      "module_id": "M_1",
      "title": "string",
      "learning_objectives": [
        {{
          "objective_id": "LO_1_1",
          "statement": "string",
          "bloom_level": "remember|understand|apply|analyze|evaluate|create",
          "assessment_method": "string"
        }}
      ],
      ...
    }}
  ],
  ...
}}

Generate the course outline now:
"""
```

**Output Validation Contract**
```python
def _validate_llm_output(self, response_text: str) -> dict:
    """
    Validate LLM output is parseable JSON.
    
    Raises:
        ValueError: If not valid JSON
        pydantic.ValidationError: If not valid schema
    """
    
    # Step 1: Is it valid JSON?
    try:
        outline_dict = json.loads(response_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM output not valid JSON: {e}")
    
    # Step 2: Does it match our schema?
    try:
        outline = CourseOutlineSchema(**outline_dict)
    except pydantic.ValidationError as e:
        raise ValueError(f"LLM output doesn't match schema: {e}")
    
    # Step 3: Are all constraints respected?
    self._check_constraints(outline)
    
    return json.loads(outline.json())

def _check_constraints(self, outline: CourseOutlineSchema) -> None:
    """Verify generated outline respects input constraints."""
    
    # Check: Right number of modules?
    assert 2 <= len(outline.modules) <= 6, f"Expected 2-6 modules, got {len(outline.modules)}"
    
    # Check: Right total duration?
    total_hours = sum(m.estimated_hours for m in outline.modules)
    assert abs(total_hours - self.context.user_input.duration_hours) < 1.0, \
        f"Duration mismatch: {total_hours} != {self.context.user_input.duration_hours}"
    
    # Check: All modules have objectives?
    for module in outline.modules:
        assert 3 <= len(module.learning_objectives) <= 7, \
            f"Module {module.module_id} has {len(module.learning_objectives)} LOs, expected 3-7"
    
    # Check: Assessments present?
    for module in outline.modules:
        assert module.assessment is not None, f"Module {module.module_id} missing assessment"
```

**Exit Criteria for Step 2.6**
- [ ] Prompt is deterministic (same input → same structure)
- [ ] Output always valid JSON (enforced)
- [ ] Schema validation always passes (enforced)
- [ ] Constraints checked before returning (enforced)
- [ ] Bad LLM output fails fast (with clear error)
- [ ] Constraint checks ≤ 30 lines (readable)

**Tests Required**
```python
def test_prompt_generates_valid_json():
    """LLM prompt always produces valid JSON."""
    agent = CoreModuleCreationAgent()
    prompt = agent._build_prompt(valid_schema)
    
    # Verify prompt structure
    assert "JSON" in prompt
    assert "modules" in prompt
    assert "learning_objectives" in prompt

def test_output_validation_rejects_invalid_json():
    """Invalid JSON rejected with clear error."""
    agent = CoreModuleCreationAgent()
    
    with pytest.raises(ValueError, match="not valid JSON"):
        agent._validate_llm_output("{ invalid json }")

def test_output_validation_rejects_schema_mismatch():
    """Schema mismatch rejected with clear error."""
    agent = CoreModuleCreationAgent()
    
    invalid_outline = '{"course_title": "Test"}'  # Missing required fields
    
    with pytest.raises(ValueError, match="doesn't match schema"):
        agent._validate_llm_output(invalid_outline)

def test_constraint_check_rejects_wrong_module_count():
    """Wrong module count rejected."""
    agent = CoreModuleCreationAgent()
    
    outline = create_test_outline(num_modules=1)  # Too few
    
    with pytest.raises(AssertionError, match="Expected 2-6 modules"):
        agent._check_constraints(outline)

def test_constraint_check_rejects_wrong_duration():
    """Wrong duration rejected."""
    agent = CoreModuleCreationAgent()
    
    outline = create_test_outline(total_hours=500)  # Way too much
    
    with pytest.raises(AssertionError, match="Duration mismatch"):
        agent._check_constraints(outline)
```

**Files Affected**
- `agents/module_creation_agent.py` - _build_prompt(), _validate_llm_output(), _check_constraints()

---

### 🔹 STEP 2.7 — Wire Orchestrator → Agent → Service

**Responsibility:** Connect all components in real execution flow

**Full Execution Chain**
```
UI Form (Streamlit)
    ↓
(user clicks "Generate")
    ↓
app.py: main() → st.session_state["orchestrator"].run(user_input)
    ↓
orchestrator.py: CourseOrchestratorAgent.run(user_input)
    ├─ Build ExecutionContext
    ├─ Call module_agent.run(context)
    ├─ Validate output
    └─ Return CourseOutlineSchema
    ↓
module_creation_agent.py: CoreModuleCreationAgent.run(context)
    ├─ Build prompt
    ├─ Call llm_service.generate()
    ├─ Parse JSON
    ├─ Validate schema
    └─ Return CourseOutlineSchema
    ↓
llm_service.py: get_llm_service().generate(prompt, system_prompt)
    ├─ Select model (from env)
    ├─ Call OpenAI/Anthropic/Ollama API
    └─ Return LLMResponse
    ↓
ModuleCreationAgent receives LLMResponse
    ❌ JSON parsing fails → ValueError
    ✅ JSON valid → parse to dict
    ❌ Schema mismatch → ValidationError
    ✅ Schema valid → return CourseOutlineSchema
    ↓
Orchestrator receives CourseOutlineSchema
    ✅ Valid → return to caller
    ❌ Invalid → ValueError (shouldn't happen)
    ↓
app.py receives CourseOutlineSchema
    ✓ Store in session
    ✓ Render to UI
```

**Code Integration Points**

**1. app.py (Existing, Minimal Changes)**
```python
# In render_output_panel or main()
@st.cache_resource
def get_orchestrator():
    """Get cached orchestrator instance."""
    return CourseOrchestratorAgent()

# In main()
if submitted_form:
    try:
        with st.spinner("⏳ Generating course outline..."):
            orchestrator = get_orchestrator()
            
            outline = await asyncio.run(
                orchestrator.run(
                    user_input=user_input,
                    session_id=session_id,
                )
            )
            
            st.success("✅ Course outline generated!")
            st.balloons()
            
            # Store in session
            st.session_state["current_outline"] = outline.dict()
            
            # Render output
            render_output_panel(outline)
            
    except Exception as e:
        st.error(f"❌ Generation failed: {str(e)}")
        if st.session_state.get("debug_mode"):
            st.exception(e)
```

**2. orchestrator.py (New Phase 2 Version)**
```python
from services import get_llm_service
from schemas.execution_context import ExecutionContext
import logging

logger = logging.getLogger(__name__)

class CourseOrchestratorAgent:
    """Single-pass orchestrator (Phase 2)."""
    
    def __init__(self):
        self.module_agent = CoreModuleCreationAgent()
        self.logger = logger
    
    async def run(
        self,
        user_input: Union[UserInputSchema, dict],
        session_id: Optional[str] = None,
    ) -> CourseOutlineSchema:
        """
        Route user input → module agent → outline.
        
        Args:
            user_input: Educator requirements
            session_id: For logging
            
        Returns:
            CourseOutlineSchema
        """
        
        # Step 1: Normalize input
        if isinstance(user_input, dict):
            user_input = UserInputSchema(**user_input)
        elif not isinstance(user_input, UserInputSchema):
            raise ValueError(f"Invalid input type: {type(user_input)}")
        
        # Step 2: Build context
        context = ExecutionContext(
            user_input=user_input,
            session_id=session_id or str(uuid.uuid4()),
            execution_id=str(uuid.uuid4()),
            execution_mode="single_pass",
        )
        
        # Step 3: Log start
        self.logger.info(
            f"Starting orchestration",
            extra={
                "execution_id": context.execution_id,
                "course_title": user_input.course_title,
                "duration_hours": user_input.duration_hours,
            }
        )
        
        # Step 4: Call module agent (phase 2: only one agent)
        try:
            outline = await self.module_agent.run(context)
        except Exception as e:
            self.logger.error(
                f"Module agent failed: {str(e)}",
                extra={"execution_id": context.execution_id}
            )
            raise
        
        # Step 5: Log completion
        self.logger.info(
            f"Orchestration complete",
            extra={
                "execution_id": context.execution_id,
                "modules": len(outline.modules),
            }
        )
        
        return outline
```

**3. module_creation_agent.py (New Phase 2 Version)**
```python
from services import get_llm_service
from schemas.execution_context import ExecutionContext
import json

class CoreModuleCreationAgent:
    """LLM-powered module creation."""
    
    async def run(self, context: ExecutionContext) -> CourseOutlineSchema:
        """Generate course outline using LLM."""
        
        user_input = context.user_input
        
        # Step 1: Build prompt
        prompt = self._build_prompt(user_input)
        
        # Step 2: Call LLM
        llm = get_llm_service()
        response = await llm.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            max_tokens=context.max_tokens,
        )
        
        # Step 3: Validate & parse
        outline = self._validate_llm_output(response.content)
        
        # Step 4: Return
        return outline
    
    def _build_prompt(self, user_input: UserInputSchema) -> str:
        # ... (see Step 2.6)
        pass
    
    def _validate_llm_output(self, response_text: str) -> CourseOutlineSchema:
        # ... (see Step 2.6)
        pass
```

**4. services/llm_service.py (Already Exists)**
- No changes needed
- Just used correctly

**Exit Criteria for Step 2.7**
- [ ] UI form submission triggers orchestrator
- [ ] Orchestrator calls module agent exactly once
- [ ] Module agent calls llm_service.generate() exactly once
- [ ] Output returned to UI for rendering
- [ ] All errors propagate with clear messages
- [ ] Logging tracks execution_id through all layers

**Tests Required**
```python
@pytest.mark.asyncio
async def test_orchestrator_to_llm_flow():
    """Full chain: Orchestrator → Agent → LLM → Output."""
    
    # Mock LLM
    mock_response = LLMResponse(
        content=json.dumps(VALID_COURSE_OUTLINE_DICT),
        tokens_used=1234,
        model="gpt-4",
    )
    mock_llm = create_mock_llm([mock_response])
    set_llm_service(mock_llm)
    
    # Execute
    orchestrator = CourseOrchestratorAgent()
    outline = await orchestrator.run(valid_user_input)
    
    # Verify
    assert isinstance(outline, CourseOutlineSchema)
    assert outline.course_title == valid_user_input.course_title
    assert len(outline.modules) >= 2
    assert mock_llm.generate_called

@pytest.mark.asyncio
async def test_llm_timeout_propagates():
    """LLM timeout surfaces as TimeoutError."""
    
    mock_llm = create_mock_llm([TimeoutError("API timeout")])
    set_llm_service(mock_llm)
    
    orchestrator = CourseOrchestratorAgent()
    
    with pytest.raises(TimeoutError):
        await orchestrator.run(valid_user_input)

@pytest.mark.asyncio
async def test_invalid_llm_output_fails_fast():
    """Invalid LLM output caught and reported."""
    
    mock_response = LLMResponse(
        content="{ invalid json }",  # Bad JSON
        tokens_used=100,
        model="gpt-4",
    )
    mock_llm = create_mock_llm([mock_response])
    set_llm_service(mock_llm)
    
    orchestrator = CourseOrchestratorAgent()
    
    with pytest.raises(ValueError, match="not valid JSON"):
        await orchestrator.run(valid_user_input)
```

**Files Affected**
- `app.py` - Integrate orchestrator.run() on form submit
- `agents/orchestrator.py` - Full Phase 2 implementation
- `agents/module_creation_agent.py` - Full Phase 2 implementation
- `schemas/execution_context.py` - Create ExecutionContext dataclass

---

### 🔹 STEP 2.8 — Streamlit Output Rendering (Read-Only)

**Responsibility:** Display generated outline beautifully (no editing yet)

**Current State**
- ✅ Output panel exists from Phase 1
- ✅ Renders mock CourseOutlineSchema
- ✅ Expandable modules, metrics, etc.

**Phase 2 Changes: None Required**
- Output panel works with real outlines exactly like mock outlines
- Both are `CourseOutlineSchema` instances

**Verification Checklist**
```python
# Real outline from LLM
outline = CourseOutlineSchema(
    course_title="...",
    modules=[Module(...), Module(...)],
    ...
)

# Mock outline from Phase 1
mock_outline = CourseOutlineSchema(
    course_title="...",
    modules=[Module(...), Module(...)],
    ...
)

# Both render identically via render_output_panel(outline)
# No code changes needed!
```

**Output Panel Features (Already Working)**
- ✅ Course metrics (duration, module count, LO count)
- ✅ Course summary
- ✅ Audience info display
- ✅ Learning outcomes list
- ✅ Expandable modules (accordion)
  - Learning objectives
  - Lessons (with duration)
  - Assessment info
- ✅ Capstone project
- ✅ Recommended tools
- ✅ Instructor notes
- ✅ Debug panel (raw JSON)

**Phase 2 Focus: Error States**

New error rendering:
```python
def render_error_state(error_message: str, debug_mode: bool = False):
    """Show friendly error to user."""
    
    st.error(f"❌ {error_message}")
    
    if debug_mode:
        st.info("Debug Info (Hidden in Production):")
        st.code(traceback.format_exc())

# Usage in app.py
except ValueError as e:
    render_error_state(
        error_message="Failed to generate outline. Please check your inputs.",
        debug_mode=st.session_state.get("debug_mode", False)
    )
except TimeoutError:
    render_error_state(
        error_message="Generation took too long. Please try again.",
        debug_mode=st.session_state.get("debug_mode", False)
    )
```

**Exit Criteria for Step 2.8**
- [ ] Real LLM output renders without crash
- [ ] Error states display friendly messages
- [ ] Debug mode shows raw errors + stack trace
- [ ] No editing UI (buttons, modals, etc.)
- [ ] Scrollable for long outline
- [ ] Mobile responsive (Streamlit default)

**Tests Required**
```python
def test_output_panel_renders_real_outline():
    """Real LLM outline renders correctly."""
    
    # Get real outline from Phase 1 test
    outline = create_valid_course_outline()
    
    # Should render without error (tested manually or via Streamlit testing)
    # render_output_panel(outline)  # Can't easily test UI in pytest

def test_error_message_friendly():
    """Error message is user-friendly."""
    
    error_msg = "Invalid course duration"
    
    # render_error_state(error_msg)
    # Verify UI shows user-friendly message, not traceback
```

**Files Affected**
- `app.py` - Error handling with render_error_state()
- No changes to render_output_panel() needed

---

### 🔹 STEP 2.9 — Phase-2 Error Handling Strategy

**Responsibility:** Prevent silent failures and crashes

**Error Hierarchy**

**Tier 1: Input Validation (User's Fault)**
```python
# Caught in app.py form validation (Phase 1)
# Example: Missing required field

if not user_input.course_title:
    st.error("❌ Please enter a course title")
    return
```

**Tier 2: LLM Failures (Service's Fault)**
```python
# Caught in orchestrator/agent
# Example: API key missing, timeout, rate limit

try:
    response = await llm.generate(prompt)
except TimeoutError:
    raise TimeoutError("LLM response took >30s")
except Exception as e:
    raise RuntimeError(f"LLM failed: {str(e)}")
```

**Tier 3: Output Invalid (LLM's Fault)**
```python
# Caught in module_creation_agent
# Example: Invalid JSON, schema mismatch

try:
    outline_dict = json.loads(llm_response)
except json.JSONDecodeError:
    raise ValueError("LLM returned invalid JSON")

try:
    outline = CourseOutlineSchema(**outline_dict)
except pydantic.ValidationError:
    raise ValueError("LLM output doesn't match schema")
```

**Tier 4: Unexpected (Bug)**
```python
# Uncaught exceptions → user sees generic error
# Example: AttributeError, TypeError

# Should NOT happen in Phase 2
```

**Error Handling in app.py**

```python
async def generate_outline_safe(user_input, session_id):
    """Generate outline with comprehensive error handling."""
    
    orchestrator = get_orchestrator()
    
    try:
        # Attempt generation
        outline = await orchestrator.run(
            user_input=user_input,
            session_id=session_id,
        )
        
        # Success path
        st.success("✅ Course outline generated successfully!")
        st.balloons()
        return outline
        
    except ValueError as e:
        # Tier 3: Output invalid
        st.error(f"❌ Invalid course outline: {str(e)}")
        if st.session_state.get("debug_mode"):
            st.write("Error details:", e)
        return None
        
    except TimeoutError:
        # Tier 2: LLM timeout
        st.error("❌ Generation took too long. Please try again.")
        if st.session_state.get("debug_mode"):
            st.write("LLM timed out after 30 seconds")
        return None
        
    except RuntimeError as e:
        # Tier 2: Other LLM failures
        st.error(f"❌ Could not reach AI service: {str(e)}")
        if st.session_state.get("debug_mode"):
            st.exception(e)
        return None
        
    except Exception as e:
        # Tier 4: Unexpected (bug)
        st.error("❌ Unexpected error. Please contact support.")
        st.exception(e)  # Always show traceback for bugs
        return None
```

**Error Message Examples**

| Scenario | User Message | Debug Info |
|----------|--------------|-----------|
| Missing API key | "AI service not configured. Contact admin." | API_KEY env var missing |
| Rate limited | "Too many requests. Please wait a minute." | HTTP 429 |
| Invalid JSON | "Generation failed. Please try again." | JSON decode error + raw response |
| Schema mismatch | "Invalid outline structure. LLM error." | Validation error details |
| Timeout | "Generation took too long. Try again." | LLM hung >30s |
| Network error | "Connection failed. Check your internet." | Connection traceback |

**Exit Criteria for Step 2.9**
- [ ] All exceptions caught (no uncaught exceptions reach UI)
- [ ] User sees friendly error (no JSON traces)
- [ ] Debug mode shows detailed error info
- [ ] Errors logged with execution_id for debugging
- [ ] App doesn't crash on any error
- [ ] Error messages are actionable (not "Error: True")

**Tests Required**
```python
@pytest.mark.asyncio
async def test_llm_timeout_friendly_error():
    """Timeout error surfaces as friendly message."""
    
    mock_llm = create_mock_llm([TimeoutError()])
    set_llm_service(mock_llm)
    
    try:
        await orchestrator.run(valid_input)
        assert False, "Should have raised"
    except TimeoutError as e:
        assert "timeout" in str(e).lower() or "too long" in str(e).lower()

@pytest.mark.asyncio
async def test_invalid_json_friendly_error():
    """Invalid JSON error surfaces with clear message."""
    
    mock_response = LLMResponse(
        content="{ not valid }",
        tokens_used=100,
        model="gpt-4",
    )
    mock_llm = create_mock_llm([mock_response])
    set_llm_service(mock_llm)
    
    try:
        await orchestrator.run(valid_input)
        assert False, "Should have raised"
    except ValueError as e:
        assert "JSON" in str(e) or "json" in str(e)

def test_error_message_no_json_dumps():
    """Error messages don't expose raw JSON."""
    
    error_msg = format_error_for_user(
        ValueError("JSON decode error: ...")
    )
    
    assert "{" not in error_msg
    assert "error" in error_msg.lower()
```

**Files Affected**
- `agents/orchestrator.py` - Try/catch with proper exceptions
- `agents/module_creation_agent.py` - Try/catch with proper exceptions
- `app.py` - generate_outline_safe() function

---

### 🔹 STEP 2.10 — Phase-2 Test Suite (Mandatory Gate)

**Responsibility:** Lock correctness before moving to Phase 3

**Test File:** `tests/test_phase_2_orchestrator.py`

**Test Coverage Map**

```python
# 1. ORCHESTRATOR TESTS (3 tests)

def test_orchestrator_calls_module_agent_once():
    """Orchestrator calls exactly one agent."""
    # Verify: No validation agent, no search, no retrieval
    # Only ModuleCreationAgent called
    
def test_orchestrator_builds_context_correctly():
    """ExecutionContext built with all fields."""
    # Verify: session_id, execution_id, user_input correct
    
def test_orchestrator_passes_context_to_agent():
    """Context passed to agent (not raw input)."""
    # Verify: Agent receives ExecutionContext, not dict

# 2. MODULE AGENT TESTS (3 tests)

def test_module_agent_calls_llm_service():
    """Agent uses llm_service.generate(), not SDK."""
    # Verify: get_llm_service() called, not openai.ChatCompletion
    
def test_module_agent_returns_valid_schema():
    """Output is valid CourseOutlineSchema."""
    # Verify: CourseOutlineSchema(**output) succeeds
    
def test_module_agent_respects_constraints():
    """Generated outline respects user constraints."""
    # Verify: Module count, duration, depth, etc. correct

# 3. LLM SERVICE TESTS (2 tests)

def test_llm_service_mock():
    """Mock LLM service works for testing."""
    # Verify: Can inject mock without code changes
    
def test_llm_service_provider_swap():
    """Can swap provider via env without code changes."""
    # Verify: OPENAI → ANTHROPIC works

# 4. EXECUTION CONTEXT TESTS (2 tests)

def test_execution_context_serializable():
    """Context serializes to dict for logging."""
    
def test_execution_context_with_missing_pdf():
    """PDF optional, doesn't break context."""

# 5. ERROR HANDLING TESTS (3 tests)

def test_invalid_llm_output_rejected():
    """Invalid JSON from LLM rejected with ValueError."""
    
def test_schema_mismatch_rejected():
    """LLM output missing required fields rejected."""
    
def test_constraint_violation_rejected():
    """Wrong module count / duration rejected."""

# 6. END-TO-END TESTS (2 tests)

def test_ui_to_outline_flow():
    """Full flow: UserInputSchema → Orchestrator → CourseOutlineSchema."""
    
def test_single_pass_enforcement():
    """Only one agent called in Phase 2."""
    # Verify: No loops, no retries, no sub-agents

# Total: 15 tests covering all Phase 2 components
```

**Test Structure**

```python
# tests/test_phase_2_orchestrator.py

import pytest
from agents.orchestrator import CourseOrchestratorAgent
from agents.module_creation_agent import CoreModuleCreationAgent
from schemas.execution_context import ExecutionContext
from schemas.user_input import UserInputSchema
from schemas.course_outline import CourseOutlineSchema
from services import (
    get_llm_service, set_llm_service, MockLLMService
)
import json


class TestPhase2Orchestrator:
    """Orchestrator tests."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_single_pass(self):
        """Orchestrator calls exactly ONE agent."""
        # Setup
        mock_llm = MockLLMService(VALID_RESPONSE)
        set_llm_service(mock_llm)
        
        # Execute
        orchestrator = CourseOrchestratorAgent()
        outline = await orchestrator.run(valid_input, session_id="s1")
        
        # Verify: Only one agent call
        assert mock_llm.call_count == 1
        assert outline is not None

    @pytest.mark.asyncio
    async def test_orchestrator_builds_context(self):
        """ExecutionContext built correctly."""
        orchestrator = CourseOrchestratorAgent()
        
        # Should build context with execution_id, session_id, etc.
        # (tested internally in run method)

    @pytest.mark.asyncio
    async def test_orchestrator_validates_output(self):
        """Orchestrator validates outline against schema."""
        mock_llm = MockLLMService(INVALID_RESPONSE)  # Missing fields
        set_llm_service(mock_llm)
        
        orchestrator = CourseOrchestratorAgent()
        
        with pytest.raises(ValueError):
            await orchestrator.run(valid_input)


class TestPhase2ModuleAgent:
    """Module creation agent tests."""
    
    @pytest.mark.asyncio
    async def test_agent_uses_llm_service(self):
        """Agent calls llm_service.generate()."""
        mock_llm = MockLLMService(VALID_RESPONSE)
        set_llm_service(mock_llm)
        
        agent = CoreModuleCreationAgent()
        context = ExecutionContext(
            user_input=valid_input,
            session_id="s1",
        )
        
        outline = await agent.run(context)
        
        # Verify LLM was called
        assert mock_llm.was_called
        assert isinstance(outline, CourseOutlineSchema)

    @pytest.mark.asyncio
    async def test_agent_respects_duration_constraint(self):
        """Agent generates right number of modules."""
        mock_llm = MockLLMService(VALID_RESPONSE)
        set_llm_service(mock_llm)
        
        agent = CoreModuleCreationAgent()
        
        # Short course
        short_input = UserInputSchema(..., duration_hours=10)
        context = ExecutionContext(user_input=short_input, session_id="s1")
        short_outline = await agent.run(context)
        
        # Long course
        long_input = UserInputSchema(..., duration_hours=100)
        context = ExecutionContext(user_input=long_input, session_id="s1")
        long_outline = await agent.run(context)
        
        # Verify: More hours → more modules (generally)
        assert len(short_outline.modules) >= 2
        assert len(long_outline.modules) >= 2

    @pytest.mark.asyncio
    async def test_agent_rejects_invalid_json(self):
        """Invalid JSON from LLM rejected."""
        mock_llm = MockLLMService("{ invalid json }")
        set_llm_service(mock_llm)
        
        agent = CoreModuleCreationAgent()
        context = ExecutionContext(user_input=valid_input, session_id="s1")
        
        with pytest.raises(ValueError, match="JSON"):
            await agent.run(context)


class TestPhase2LLMService:
    """LLM service integration tests."""
    
    @pytest.mark.asyncio
    async def test_mock_llm_service(self):
        """Mock LLM works for testing."""
        mock_llm = MockLLMService(VALID_RESPONSE)
        set_llm_service(mock_llm)
        
        llm = get_llm_service()
        response = await llm.generate("test")
        
        assert response is not None
        assert response.content == VALID_RESPONSE


class TestPhase2EndToEnd:
    """End-to-end integration tests."""
    
    @pytest.mark.asyncio
    async def test_full_generation_flow(self):
        """UI → Orchestrator → LLM → Outline."""
        mock_llm = MockLLMService(VALID_RESPONSE)
        set_llm_service(mock_llm)
        
        # User submits form
        user_input = UserInputSchema(
            course_title="Python 101",
            course_description="Learn Python",
            audience_level=AudienceLevel.BEGINNER,
            audience_category=AudienceCategory.COLLEGE_STUDENTS,
            learning_mode=LearningMode.PRACTICAL_HANDS_ON,
            depth_requirement=DepthRequirement.INTRODUCTORY,
            duration_hours=40,
        )
        
        # Orchestrator runs
        orchestrator = CourseOrchestratorAgent()
        outline = await orchestrator.run(user_input, session_id="s1")
        
        # Output is valid
        assert isinstance(outline, CourseOutlineSchema)
        assert outline.course_title == "Python 101"
        assert len(outline.modules) >= 2
        assert outline.total_duration_hours == 40

    @pytest.mark.asyncio
    async def test_single_agent_called(self):
        """Verify Phase 2 constraint: Only one agent called."""
        call_log = []
        
        # Mock agents to log calls
        original_module_agent = CoreModuleCreationAgent.run
        
        async def logged_agent_run(self, context):
            call_log.append("module_agent")
            return await original_module_agent(self, context)
        
        CoreModuleCreationAgent.run = logged_agent_run
        
        # Execute
        mock_llm = MockLLMService(VALID_RESPONSE)
        set_llm_service(mock_llm)
        
        orchestrator = CourseOrchestratorAgent()
        await orchestrator.run(valid_input)
        
        # Verify: Only module agent called
        assert call_log == ["module_agent"]
        assert len(call_log) == 1  # Exactly one


# Test Fixtures

@pytest.fixture
def valid_input():
    """Valid user input for testing."""
    return UserInputSchema(
        course_title="Test Course",
        course_description="Test description",
        audience_level=AudienceLevel.INTERMEDIATE,
        audience_category=AudienceCategory.COLLEGE_STUDENTS,
        learning_mode=LearningMode.HYBRID,
        depth_requirement=DepthRequirement.CONCEPTUAL,
        duration_hours=40,
    )


VALID_RESPONSE = """{
  "course_title": "Test Course",
  "course_summary": "Test summary",
  "audience_level": "intermediate",
  "audience_category": "college_students",
  "learning_mode": "hybrid",
  "depth_requirement": "conceptual",
  "total_duration_hours": 40,
  "prerequisites": [],
  "course_level_learning_outcomes": [...],
  "modules": [
    {
      "module_id": "M_1",
      "title": "Module 1",
      "synopsis": "Test",
      "estimated_hours": 20,
      "learning_objectives": [...],
      "lessons": [...],
      "assessment": {...}
    },
    {
      "module_id": "M_2",
      "title": "Module 2",
      "synopsis": "Test",
      "estimated_hours": 20,
      "learning_objectives": [...],
      "lessons": [...],
      "assessment": {...}
    }
  ],
  "capstone_project": null,
  "evaluation_strategy": {},
  "recommended_tools": [],
  "instructor_notes": null,
  "citations_and_provenance": [],
  "generated_by_agent": "module_creation_agent",
  "generation_timestamp": null
}"""

INVALID_RESPONSE = '{"course_title": "Missing modules"}'  # Schema violation
```

**Exit Criteria for Step 2.10 (Strict Gate)**

Must ALL pass before moving to Phase 3:

- [ ] **15/15 tests pass** (100% success rate)
- [ ] **Zero test flakes** (run 3x, same results)
- [ ] **Code coverage ≥ 80%** for new code
  - orchestrator.py: 100%
  - module_creation_agent.py: 100%
  - execution_context.py: 100%
- [ ] **One-click generation works** (UI to outline)
- [ ] **Output schema valid** every time
- [ ] **No unused imports** in agents
- [ ] **No dead code** (Phase 1 mock methods removed)
- [ ] **All error paths tested**
- [ ] **Logs track execution_id**
- [ ] **LLM service swappable** (tested with mock + real)

**Test Execution Command**
```bash
# Run Phase 2 tests
python -m pytest tests/test_phase_2_orchestrator.py -v --tb=short

# With coverage
python -m pytest tests/test_phase_2_orchestrator.py --cov=agents --cov=schemas --cov=services --cov-report=term-missing
```

**Expected Output**
```
tests/test_phase_2_orchestrator.py::TestPhase2Orchestrator::test_orchestrator_single_pass PASSED
tests/test_phase_2_orchestrator.py::TestPhase2Orchestrator::test_orchestrator_builds_context PASSED
tests/test_phase_2_orchestrator.py::TestPhase2Orchestrator::test_orchestrator_validates_output PASSED
tests/test_phase_2_orchestrator.py::TestPhase2ModuleAgent::test_agent_uses_llm_service PASSED
tests/test_phase_2_orchestrator.py::TestPhase2ModuleAgent::test_agent_respects_duration_constraint PASSED
tests/test_phase_2_orchestrator.py::TestPhase2ModuleAgent::test_agent_rejects_invalid_json PASSED
tests/test_phase_2_orchestrator.py::TestPhase2LLMService::test_mock_llm_service PASSED
tests/test_phase_2_orchestrator.py::TestPhase2EndToEnd::test_full_generation_flow PASSED
tests/test_phase_2_orchestrator.py::TestPhase2EndToEnd::test_single_agent_called PASSED
...
====================== 15 passed in 2.34s ======================
```

**Files Affected**
- `tests/test_phase_2_orchestrator.py` - NEW, 800+ lines

---

## 📊 PHASE 2 ARTIFACT SUMMARY

### Files to Create/Modify

| File | Status | Changes |
|------|--------|---------|
| `schemas/execution_context.py` | 🆕 NEW | ExecutionContext dataclass (50 lines) |
| `agents/orchestrator.py` | 📝 REWRITE | Phase 2 implementation (60 lines) |
| `agents/module_creation_agent.py` | 📝 REWRITE | LLM-powered, remove mock (250 lines) |
| `app.py` | 🔧 MINOR | Integrate orchestrator.run() (5 line change) |
| `tests/test_phase_2_orchestrator.py` | 🆕 NEW | 15 comprehensive tests (500 lines) |
| `.env.example` | 🔧 UPDATE | Add LLM_* env vars documented |
| `requirements.txt` | 🔧 UPDATE | (depends on LLM library chosen) |

**Total New Lines:** ~700 lines (schemas, orchestrator, agent)  
**Total Test Lines:** ~500 lines (15 tests)

---

## 🎯 PHASE 2 SUCCESS CRITERIA (Final Gate)

### Functional
- ✅ UI form submission → generates outline end-to-end
- ✅ Outline matches schema exactly every time
- ✅ Respects all user constraints (duration, audience, depth, mode)
- ✅ Uses real LLM calls (not templates)
- ✅ Single-pass execution (no loops, no retries)

### Technical
- ✅ LLMService used exclusively (no direct SDK imports)
- ✅ Orchestrator is traffic controller only
- ✅ ModuleCreationAgent has all intelligence
- ✅ ExecutionContext standardizes agent interfaces
- ✅ Errors fail-fast with user-friendly messages

### Testing
- ✅ 15/15 tests pass (100%)
- ✅ Zero flakes (deterministic)
- ✅ All constraints enforced in tests
- ✅ Error paths tested
- ✅ ≥80% code coverage

### Code Quality
- ✅ No dead code (Phase 1 mock removed)
- ✅ No unused imports
- ✅ Clear docstrings + boundary docs
- ✅ Logging tracks execution_id
- ✅ All Phase 3+ agent stubs remain in place

---

## 🚀 PHASE 2 → PHASE 3 Handoff

At end of Phase 2, ready to add:

**Phase 3 (Retrieval Agent):**
- ✅ ExecutionContext already supports retrieved_documents field
- ✅ ModuleCreationAgent can accept docs in prompt
- ✅ No orchestrator changes needed

**Phase 4 (Web Search Agent):**
- ✅ ExecutionContext already supports web_search_results field
- ✅ Orchestrator calls SearAgent before ModuleAgent
- ✅ Results passed via context

**Phase 6 (Validator + Retry):**
- ✅ Orchestrator adds ValidatorAgent call
- ✅ Context updated with validator_feedback
- ✅ Retry loop in orchestrator

---

## 📚 KNOWLEDGE BASE Integration

When user provides KB IDs, insert here:

**KB Topics for Phase 2:**
- [ ] KB ID: `__________` - LLM prompt engineering best practices
- [ ] KB ID: `__________` - Structured output generation from LLMs
- [ ] KB ID: `__________` - Error handling in agent systems
- [ ] KB ID: `__________` - Streamlit + backend integration patterns

---

## ✅ SIGN-OFF

**Phase 2 Plan Complete & Ready for Implementation**

- ✅ All 10 steps clearly defined
- ✅ Responsibilities assigned
- ✅ Success criteria explicit
- ✅ Tests specified upfront (TDD)
- ✅ Error handling planned
- ✅ Boundaries locked (no Phase 3+ features)
- ✅ LLMService leveraged correctly
- ✅ Schema integration verified
- ✅ Phase 3+ compatibility ensured
- ✅ Agent creep prevented

**Status:** 📋 Ready for implementation  
**Next Action:** User provides KB IDs (optional) or approves plan  
**Timeline:** Estimated 4-6 hours implementation

---

**Generated:** February 21, 2026  
**Plan Version:** 2.0 (Aligned with Services + Phase 1)  
**Target:** Single-Pass MVP Complete
