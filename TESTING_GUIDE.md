# Phase 5 Testing & Execution Guide

## Overview
Complete step-by-step guide to test the course AI agent with Phase 5 Module Creation Agent and Gemini integration.

---

## Prerequisites

### 1. Python Environment
- Python 3.10+
- pip or conda

### 2. API Keys Required
- **Gemini API Key** (Google AI Studio)
  - Get it from: https://aistudio.google.com/app/apikeys
  - Free tier available
  - NO credit card required for initial free tier

### 3. System Setup

```bash
# Navigate to project
cd c:\Users\nisha\Projects\tcs_ai\course_ai_agent

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# Or on Mac/Linux:
source venv/bin/activate
```

---

## Step 1: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Additional packages needed
pip install google-generativeai  # For Gemini support
pip install python-dotenv        # For .env config
pip install streamlit            # For UI
```

### Check if packages installed:
```bash
python -c "import google.generativeai; import streamlit; print('✓ All packages installed')"
```

---

## Step 2: Configure Environment

### Update `.env` file

Edit `c:\Users\nisha\Projects\tcs_ai\course_ai_agent\.env`:

```dotenv
# ========== LLM Configuration (Gemini) ==========
LLM_PROVIDER=gemini
LLM_MODEL=gemini-1.5-pro
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=8000
GOOGLE_API_KEY=your_gemini_api_key_here  # Replace with actual key

# ========== Optional: ChromaDB for Retrieval ==========
CHROMA_DB_PATH=./data/chroma_db
CHROMA_COLLECTION=course_curricula

# ========== Optional: Web Search ==========
TAVILY_API_KEY=optional_for_phase_4

# ========== Logging ==========
LOG_LEVEL=INFO
```

**Getting Your Gemini API Key:**
1. Go to https://aistudio.google.com/app/apikeys
2. Click "Create API Key" button
3. Copy the key
4. Paste in `.env` file as `GOOGLE_API_KEY`

---

## Step 3: Verify Setup

### Check all imports:
```bash
python -c "
from services.llm_service import get_llm_service, LLMFactory, GeminiService
from agents.module_creation_agent import get_module_creation_agent
from schemas.course_outline import CourseOutlineSchema
from utils.duration_allocator import DurationAllocator
from utils.learning_mode_templates import LearningModeTemplates
print('✓ All imports successful')
"
```

### Test LLM connection:
```bash
python -c "
import asyncio
from services.llm_service import get_llm_service

async def test():
    service = get_llm_service()
    print(f'✓ LLM Service initialized: {service.provider}')
    response = await service.generate('Say hello!')
    print(f'✓ LLM Response: {response.content[:50]}...')

asyncio.run(test())
"
```

---

## Step 4: Run Tests

### Run Quick Tests (Recommended First):
```bash
# Test only Phase 5 core functionality
pytest tests/test_phase_5_module_creation.py -v -k "schema or allocator or template"

# Expected: ~15 tests pass in 5-10 seconds
```

### Run All Phase 5 Tests:
```bash
pytest tests/test_phase_5_module_creation.py -v

# Expected: ~25 tests pass in 10-15 seconds
```

### Run All Tests (Full Suite):
```bash
pytest tests/ -v

# Expected: 80+ tests, ~30-60 seconds
```

---

## Step 5: Test Orchestrator Pipeline

### Create a test script: `test_pipeline.py`

```python
"""
Test the complete orchestration pipeline with Phase 5
"""

import asyncio
import json
from schemas.user_input import UserInputSchema
from agents.orchestrator import CourseOrchestratorAgent

async def test_orchestrator():
    """Test orchestrator with sample input"""
    
    # Create sample input
    user_input = UserInputSchema(
        course_title="Introduction to Machine Learning",
        course_description="Learn ML fundamentals and implementation techniques",
        audience_level="undergraduate",
        audience_category="STEM",
        depth_requirement="implementation_level",
        duration_hours=40,
        learning_mode="project_based"
    )
    
    # Initialize orchestrator
    orchestrator = CourseOrchestratorAgent()
    
    print("=" * 60)
    print("ORCHESTRATOR TEST: Phase 5 Module Creation Agent")
    print("=" * 60)
    print(f"Course: {user_input.course_title}")
    print(f"Duration: {user_input.duration_hours} hours")
    print(f"Learning Mode: {user_input.learning_mode}")
    print()
    
    try:
        # Run orchestrator pipeline
        print("Running orchestration pipeline...")
        result = await orchestrator.run(user_input)
        
        # Display results
        if isinstance(result, dict):
            outline = result
        else:
            outline = result.dict() if hasattr(result, 'dict') else result
        
        print("\n" + "=" * 60)
        print("RESULT: Course Outline Generated")
        print("=" * 60)
        print(f"✓ Course Title: {outline.get('course_title', 'N/A')}")
        print(f"✓ Modules: {len(outline.get('modules', []))}")
        print(f"✓ Confidence Score: {outline.get('confidence_score', 'N/A')}")
        print(f"✓ Completeness Score: {outline.get('completeness_score', 'N/A')}")
        
        # Show module structure
        modules = outline.get('modules', [])
        if modules:
            print("\nModule Structure:")
            for i, module in enumerate(modules[:3], 1):  # Show first 3
                print(f"  {i}. {module.get('title', 'Untitled')} ({module.get('estimated_hours', 0)}h)")
                objectives = module.get('learning_objectives', [])
                print(f"     Learning Objectives: {len(objectives)}")
        
        return outlineinside
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

# Run the test
if __name__ == "__main__":
    asyncio.run(test_orchestrator())
```

### Run the test:
```bash
python test_pipeline.py
```

**Expected Output:**
```
============================================================
ORCHESTRATOR TEST: Phase 5 Module Creation Agent
============================================================
Course: Introduction to Machine Learning
Duration: 40 hours
Learning Mode: project_based

Running orchestration pipeline...

============================================================
RESULT: Course Outline Generated
============================================================
✓ Course Title: Introduction to Machine Learning
✓ Modules: 6-7
✓ Confidence Score: 0.75-0.95
✓ Completeness Score: 0.80-1.00

Module Structure:
  1. Foundations of Machine Learning (6h)
     Learning Objectives: 4
  2. Supervised Learning (7h)
     Learning Objectives: 5
  3. Unsupervised Learning (6h)
     Learning Objectives: 4
```

---

## Step 6: Run Streamlit UI

### Start the app:
```bash
streamlit run app.py
```

**Browser will open at:** http://localhost:8501

### In the UI:
1. Fill in course details:
   - Course Title
   - Description
   - Audience Level
   - Depth Requirement
   - Duration (hours)
   - Learning Mode

2. Click "Generate Course Outline"

3. See results:
   - Generated modules
   - Learning objectives
   - Lesson structure
   - Confidence metrics

---

## Step 7: View Output Schema

### The Module Creation Agent outputs this structure:

```json
{
  "course_title": "...",
  "course_summary": "...",
  "audience_level": "undergraduate",
  "modules": [
    {
      "module_id": "M_1",
      "title": "...",
      "description": "...",
      "estimated_hours": 6.0,
      "learning_objectives": [
        {
          "objective_id": "LO_1_1",
          "statement": "Understand ...",
          "bloom_level": "understand",
          "assessment_method": "Quiz"
        }
      ],
      "lessons": [
        {
          "lesson_id": "L_1_1",
          "title": "...",
          "duration_minutes": 60,
          "key_concepts": ["..."],
          "activities": ["lecture"]
        }
      ],
      "assessment_type": "quiz",
      "has_capstone": false
    }
  ],
  "confidence_score": 0.85,
  "completeness_score": 0.90,
  "references": [
    {
      "title": "...",
      "source_type": "web",
      "url": "...",
      "confidence_score": 0.95
    }
  ]
}
```

---

## Troubleshooting

### Issue: "ImportError: cannot import name 'LLMService'"
**Solution:** Already fixed in this release. Run:
```bash
pip install --upgrade google-generativeai
python -m pip install -e .
```

### Issue: "GEMINI_API_KEY not found"
**Solution:** 
1. Add to `.env` file:
```env
GOOGLE_API_KEY=your_actual_key
```
2. Or set environment variable:
```bash
set GOOGLE_API_KEY=your_actual_key    # Windows
export GOOGLE_API_KEY=your_actual_key # Mac/Linux
```

### Issue: "LLM generation failed"
**Solution:**
1. Check Gemini API availability: Run `python -c "import google.generativeai; print('✓ Gemini SDK works')"`
2. Check API key is valid: https://aistudio.google.com/
3. View logs: Check terminal output for detailed errors

### Issue: "Async runtime error"
**Solution:** Ensure you're using Python 3.10+:
```bash
python --version  # Should show 3.10 or higher
```

---

## Next Steps After Testing

1. **✅ Phase 5 Complete** - Module Creation Agent working with Gemini
2. **🔄 Phase 6** - Validator Agent (quality scoring & feedback)
3. **🔄 Phase 7** - Query Agent (interactive explanations)
4. **🔄 Phase 8** - UX Polish & exports

---

## Support

For issues:
1. Check logs in terminal
2. Verify `.env` configuration
3. Test individual components:
   - `python -c "from services.llm_service import get_llm_service; print(get_llm_service())"`
   - `python -c "from schemas.course_outline import CourseOutlineSchema; print('Schema OK')"`
4. Run tests: `pytest tests/test_phase_5_module_creation.py -v`

---

## Key Files

| File | Purpose |
|------|---------|
| `services/llm_service.py` | LLM abstraction with Gemini support |
| `agents/module_creation_agent.py` | Phase 5 core agent (580+ lines) |
| `schemas/course_outline.py` | CourseOutlineSchema with validation |
| `utils/duration_allocator.py` | Pre-LLM duration calculations |
| `utils/learning_mode_templates.py` | Mode-specific structures |
| `agents/orchestrator.py` | Orchestration pipeline (Step 6 added) |
| `tests/test_phase_5_module_creation.py` | Comprehensive test suite |
| `.env` | Environment configuration (LOCAL, never commit) |

---

## Summary

✅ **Setup**: Install dependencies + configure .env
✅ **Test**: Run pytest to verify functionality
✅ **Pipeline**: Execute test_pipeline.py to see full flow
✅ **UI**: Run `streamlit run app.py` to see results in browser

**Total time to run:** ~5-10 minutes for full test suite

---

**Status:** Phase 5 PAUSED ⏸️ (Ready to push when user confirms)
