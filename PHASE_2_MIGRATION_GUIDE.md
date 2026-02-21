# Phase 2 Migration Guide for Developers

## Quick Summary

Phase 2 replaces ad-hoc dict passing with structured `ExecutionContext` objects. This is a **breaking change** for direct agent callers, but **not** for end users (app.py interface unchanged).

## Who is Affected?

| User | Impact | Action |
|------|--------|--------|
| **End Users (Streamlit app)** | ✅ None | No changes needed |
| **Test Writers** | ⚠️ Update test calls | See "Test Migration" below |
| **Agent Integrators** | ⚠️ Update agent calls | See "Agent Call Migration" below |
| **New Feature Developers** | ✅ Follow new pattern | Use ExecutionContext from start |

## Agent Call Migration

### Before (Phase 1) - NO LONGER WORKS ❌
```python
# Direct dict passing - DEPRECATED
aggregated_inputs = {
    "user_input": user_input,
    "retrieval_results": None,
    "search_results": None,
}
outline = await agent.run(aggregated_inputs)
```

### After (Phase 2) - NEW PATTERN ✅
```python
from schemas.execution_context import ExecutionContext

# Create structured context
context = ExecutionContext(
    user_input=user_input,
    session_id="session-123",
    execution_mode="single_pass",
)

# Pass to agent
outline = await agent.run(context)
```

## Test Migration Examples

### Example 1: Orchestrator Test

**Before:**
```python
@pytest.mark.asyncio
async def test_orchestrator(self):
    orchestrator = CourseOrchestratorAgent()
    user_input = UserInputSchema(...)
    
    outline = await orchestrator.run(user_input.dict())
    assert isinstance(outline, dict)
```

**After:**
```python
@pytest.mark.asyncio
async def test_orchestrator(self):
    orchestrator = CourseOrchestratorAgent()
    user_input = UserInputSchema(...)
    
    # No changes needed! Orchestrator.run() still accepts dict
    outline = await orchestrator.run(user_input.dict())
    assert isinstance(outline, dict)
```

✅ **Orchestrator is backward compatible with app.py**

### Example 2: Module Creation Agent Test

**Before:**
```python
@pytest.mark.asyncio
async def test_module_agent(self):
    agent = CoreModuleCreationAgent()
    user_input = UserInputSchema(...)
    
    aggregated_inputs = {"user_input": user_input}
    outline = await agent.run(aggregated_inputs)  # ❌ BREAKS
```

**After:**
```python
@pytest.mark.asyncio
async def test_module_agent(self):
    from schemas.execution_context import ExecutionContext
    agent = CoreModuleCreationAgent()
    user_input = UserInputSchema(...)
    
    # Create ExecutionContext
    context = ExecutionContext(
        user_input=user_input, 
        session_id="test-session"
    )
    
    outline = await agent.run(context)
    
    # Convert to dict if needed for assertions
    if not isinstance(outline, dict):
        outline = outline.dict()
    assert isinstance(outline, dict)
```

✅ **All Phase 1 UI tests updated and passing**

## API Changes Reference

### CourseOrchestratorAgent

```python
# METHOD: run()
async def run(
    self,
    user_input: Union[UserInputSchema, dict],
    session_id: Optional[str] = None,
) -> dict:
    """
    Returns: CourseOutlineSchema as dict
    Accepts: UserInputSchema or dict (backward compatible)
    """
```

**What changed:**
- ✅ Accepts `Union[UserInputSchema, dict]` (backward compatible)
- ✅ Returns `dict` (same as before)
- ✅ Builds ExecutionContext internally
- ✅ Adds structured logging

### CoreModuleCreationAgent

```python
# METHOD: run()
async def run(self, context: ExecutionContext) -> CourseOutlineSchema:
    """
    Returns: CourseOutlineSchema object
    Accepts: ExecutionContext object
    """
```

**What changed:**
- ❌ No longer accepts dict
- ✅ Now accepts ExecutionContext
- ✅ Returns CourseOutlineSchema (not dict)
- ✅ Adds schema validation
- ✅ Adds logging with execution_id

## ExecutionContext Reference

```python
from schemas.execution_context import ExecutionContext

context = ExecutionContext(
    # REQUIRED
    user_input=UserInputSchema(...),
    session_id="user-session-123",
    
    # OPTIONAL (with defaults)
    execution_id=None,  # Auto-generated if not provided
    created_at=None,    # Auto-set to now if not provided
    execution_mode="single_pass",  # Phase 2 only
    max_tokens=8000,
    
    # OPTIONAL (Phase 3+ extensions, defaults to None)
    uploaded_pdf_text=None,
    uploaded_pdf_metadata=None,
    retrieved_documents=None,
    web_search_results=None,
)

# Access properties
print(context.execution_id)      # UUID auto-generated
print(context.user_input.course_title)
print(context.session_id)
```

## Common Errors and Solutions

### Error 1: AttributeError: 'dict' object has no attribute 'user_input'

**Cause:** Passing dict to agent expecting ExecutionContext

```python
# ❌ WRONG
context_dict = {"user_input": user_input}
outline = await agent.run(context_dict)

# ✅ CORRECT
from schemas.execution_context import ExecutionContext
context = ExecutionContext(user_input=user_input, session_id="test")
outline = await agent.run(context)
```

### Error 2: TypeError: expected ExecutionContext, got dict

**Cause:** Agent now requires ExecutionContext object

```python
# ❌ WRONG
await module_agent.run({"user_input": user_input})

# ✅ CORRECT
await module_agent.run(ExecutionContext(user_input=user_input, session_id="..."))
```

### Error 3: Agent returns CourseOutlineSchema but test expects dict

**Cause:** Module agent now returns typed object, not dict

```python
# ❌ WRONG (Agent method returns CourseOutlineSchema)
outline = await module_agent.run(context)
assert "modules" in outline  # AttributeError: dict indices

# ✅ CORRECT
outline = await module_agent.run(context)  # Returns CourseOutlineSchema
if isinstance(outline, dict):
    modules = outline["modules"]
else:
    modules = outline.modules  # Access as attribute
```

## Backward Compatibility Matrix

| Component | Phase 1 API | Phase 2 API | Impact |
|-----------|------------|------------|--------|
| `CourseOrchestratorAgent.run()` | Dict input | Dict input | ✅ Fully compatible |
| `CoreModuleCreationAgent.run()` | Dict input | ExecutionContext | ❌ Breaking change |
| `Orchestrator.run()` returns | dict | dict | ✅ Same output |
| `ModuleAgent.run()` returns | dict | CourseOutlineSchema | ⚠️ Typed object (converted to dict internally) |

## Migration Checklist

- [ ] Understand ExecutionContext schema
- [ ] Update direct agent test calls to use ExecutionContext
- [ ] Update any custom agent calls in code
- [ ] Import ExecutionContext: `from schemas.execution_context import ExecutionContext`
- [ ] Verify tests pass: `pytest tests/test_phase_1_ui.py -v`
- [ ] Run app.py: No changes needed (orchestrator is backward compatible)
- [ ] Update documentation with new pattern

## Phase 3+ Implications

**Current Phase 2 design allows Phase 3+ to be added without orchestrator changes:**

```python
# Phase 3 will work like this (no orchestrator changes needed):
# Orchestrator remains same
# Module agent gets same ExecutionContext with new fields populated

context = ExecutionContext(
    user_input=user_input,
    session_id=session_id,
    retrieved_documents=await retrieval_agent.run(...),  # Phase 3
    web_search_results=await search_agent.run(...),      # Phase 4
)
outline = await module_agent.run(context)  # Same call
```

## FAQ

**Q: Do I need to update app.py?**
A: No. The orchestrator still accepts dict from app.py internally.

**Q: Can I still pass dict to agents?**
A: No. All agents now require ExecutionContext. Translate dicts to ExecutionContext first.

**Q: What if I'm not writing tests, just using the app?**
A: No changes needed. The Streamlit app interface is unchanged.

**Q: How do I migrate existing code that calls agents directly?**
A: Replace `agent.run(dict)` with `agent.run(ExecutionContext(...))`.

**Q: Will Phase 3+ require more migration?**
A: No. ExecutionContext is designed to support Phases 3-7 without breaking changes.

## Support

For issues or questions:
1. Check PHASE_2_IMPLEMENTATION.md for architecture details
2. Review test examples in test_phase_1_ui.py
3. Read ExecutionContext docstring in schemas/execution_context.py
