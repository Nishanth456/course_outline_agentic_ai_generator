# Phase 3 RAG - Curriculum Folder Integration

## Summary: What We Just Updated

Your **Phase 3 implementation now includes curriculum loading from `data/sample_curricula` folder**. Here's what changed:

### 1. **What Exists**
✅ `data/sample_curricula/java.txt` - A real curriculum file
✅ `tools/curriculum_ingestion.py` - Has TWO methods now:
- `ingest_from_folder()` - **NEW** Reads .txt files from folder
- `ingest_example_curriculum()` - Hardcoded syllabi (backup/testing)

### 2. **How It Works**

#### Flow Chart:
```
data/sample_curricula/java.txt
        ↓
IngestionPipeline.ingest_from_folder()
        ↓
Read file + create metadata
        ↓
Clean text + chunk into ~500-word pieces  
        ↓
Create VectorDocument for each chunk (with embeddings)
        ↓
Store in ChromaDB (vector database)
        ↓
Ready for similarity search in RetrievalAgent
```

#### Code Example:
```python
# You can do this:
from tools.curriculum_ingestion import IngestionPipeline

pipeline = IngestionPipeline()

# Method 1: Load from folder (our new addition)
stored_count, docs = pipeline.ingest_from_folder("data/sample_curricula")
print(f"Stored {stored_count} chunks from folder files")

# Method 2: Hardcoded examples (fallback/testing)
stored_count, docs = pipeline.ingest_example_curriculum()
print(f"Stored {stored_count} chunks from hardcoded examples")
```

---

## Manual Testing: How to Verify It Works

### Option 1: Run the Curriculum Loading Test (RECOMMENDED)

```bash
python test_curriculum_loading.py
```

**What it does:**
1. ✅ Scans `data/sample_curricula/` folder
2. ✅ Finds `java.txt` file
3. ✅ Chunks it into 2 searchable pieces
4. ✅ Embeds each chunk with 384-D vectors
5. ✅ Stores in ChromaDB
6. ✅ Tests similarity search with 3 different queries
7. ✅ Verifies metadata is attached

**Expected Output:**
```
✅ Loaded 2 chunks from folder
✅ Vector embeddings created and indexed
✅ Similarity search working
✅ Metadata preserved
```

### Option 2: Manual Python Script

```python
#!/usr/bin/env python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from tools.curriculum_ingestion import IngestionPipeline
from services.vector_store import get_vector_store, reset_vector_store

# Initialize
reset_vector_store()
pipeline = IngestionPipeline()

# Load from folder
print("Loading curriculum from data/sample_curricula/...")
stored, docs = pipeline.ingest_from_folder("data/sample_curricula")
print(f"✅ Stored {stored} chunks")

# Query the store
store = get_vector_store()
results = store.similarity_search("object oriented programming", k=3)
print(f"Found {len(results)} results:")
for r in results:
    print(f"  - {r['metadata']['source_name']}")
    print(f"    {r['content'][:100]}...")
```

### Option 3: Run alongside Streamlit App

When you launch the app:
```bash
streamlit run app.py
```

The orchestrator will:
1. Call RetrievalAgent when generating a course
2. RetrievalAgent searches vector store (which has java.txt chunks)
3. Retrieved knowledge is passed to ModuleCreationAgent
4. Course outline incorporates retrieved curriculum

---

## What Each File Does

### `data/sample_curricula/`
```
data/sample_curricula/
├── java.txt          ← Real curriculum file (368 lines, Java fundamentals)
└── (more .txt files can be added here)
```

**You can add more files:**
- `python.txt` - Python programming curriculum
- `database.txt` - Database design curriculum
- `web_dev.txt` - Web development curriculum
- etc.

All `.txt` files in this folder will be automatically loaded and indexed!

### `tools/curriculum_ingestion.py`
Contains `IngestionPipeline` class:

**Key Method: `ingest_from_folder(folder_path)`**
```python
def ingest_from_folder(self, folder_path: str = "data/sample_curricula") -> Tuple[int, List[VectorDocument]]:
    """
    Scan and ingest all .txt files from a curriculum folder.
    
    Returns: (chunks_stored, VectorDocuments)
    """
    # 1. Find all .txt files
    # 2. For each file:
    #    - Read content
    #    - Create metadata (source_name from filename)
    #    - Chunk into ~500-word pieces
    #    - Create VectorDocuments with embeddings
    #    - Store in ChromaDB
    # 3. Return total chunks stored
```

**Result:** Each file becomes multiple searchable chunks in the vector store

---

## Current Test Results

When we ran `python test_curriculum_loading.py`:

```
Step 1: Initialize services     ✅ Done
Step 2: Load from folder        ✅ Found java.txt → 2 chunks created & stored
Step 3: Check vector store      ✅ 2 documents in ChromaDB
Step 4: Similarity search       ✅ 3 queries tested successfully
Step 5: Verify metadata         ✅ source_name, source_type, audience_level all present

RESULT: ALL PASSING ✅
```

**Key metrics:**
- 1 file found: `java.txt`
- 2 chunks created from it
- 384-D embeddings generated for each
- ChromaDB persistence working
- Search working with cosine similarity

---

## The Flow: User Request → Retrieval → Generation

```
User Request (e.g., "Teach Java OOP to beginners")
    ↓
[ExecutionContext created]
    ↓
RetrievalAgent.run(context)
    ↓
  Step 1: Generate 5 search queries:
    - "object oriented programming java"
    - "java programming basics"
    - "inheritance polymorphism"
    - "java fundamentals"
    - "java for beginners"
    ↓
  Step 2: Search vector store (ChromaDB)
    with queries + metadata filters
    ↓
  Result: Top 5 chunks from java.txt
    - Content about OOP concepts
    - Metadata: source="Java", level="beginner", domain="computer_science"
    ↓
  Step 3: Return RetrievalAgentOutput
    {
      "retrieved_chunks": [...],
      "retrieval_confidence": 0.85,
      "knowledge_summary": "Java OOP fundamentals including inheritance, polymorphism..."
    }
    ↓
[passed to ExecutionContext.retrieved_documents]
    ↓
ModuleCreationAgent.run(context)
    ↓
  Generates course outline using:
    - User requirements
    - Retrieved curriculum chunks
    ↓
Course Outline (with institutional memory!)
```

---

## How to Add More Curriculum

### Method 1: Add Text Files to Folder
```bash
# Create your curriculum file
echo "Advanced Java Design Patterns..." > data/sample_curricula/java_patterns.txt

# Next run will automatically load it
python test_curriculum_loading.py
```

### Method 2: Programmatically
```python
from tools.curriculum_ingestion import IngestionPipeline
from schemas.vector_document import VectorDocumentMetadata, SourceType, UploadedBy

pipeline = IngestionPipeline()

# Create metadata
metadata = VectorDocumentMetadata(
    institution_name="MIT",
    degree_level="graduate",
    subject_domain="computer_science",
    audience_level="advanced",
    depth_level="advanced",
    source_type=SourceType.SYLLABUS,
    uploaded_by=UploadedBy.ADMIN,
    source_name="Advanced Algorithms",
)

# Ingest content
content = "Algorithms including dynamic programming, graph theory, NP-completeness..."
stored, docs = pipeline.ingest_text(content, metadata)
print(f"Stored {stored} chunks")
```

---

## What Was Fixed

### Issue 1: VectorStore Not Reading from Folder
**Before:** Only hardcoded example syllabi
**After:** Reads all .txt files from `data/sample_curricula/`

### Issue 2: ChromaDB Deprecated Configuration
**Before:** Used old `chroma.Client(Settings(...))` API
**After:** Uses new `chroma.PersistentClient(path=...)` API

```python
# OLD (deprecated, didn't work)
client = chroma.Client(chroma.config.Settings(...))

# NEW (works with current ChromaDB)
client = chroma.PersistentClient(path=persist_directory)
```

---

## Next Steps

1. **✅ Already Done:**
   - Folder reading implemented
   - ChromaDB fixed
   - Test passes
   - `java.txt` is loadable

2. **Next: Run Full Test Suite**
   ```bash
   pytest tests/test_phase_3_retrieval.py -v
   ```
   (There are 25 tests covering all Phase 3 components)

3. **Then: Fix Your Enum Values**
   The smoke test had `TECHNICAL` but should be `COLLEGE_STUDENTS` or similar:
   ```python
   # WRONG
   audience_category=AudienceCategory.TECHNICAL
   
   # CORRECT options:
   audience_category=AudienceCategory.COLLEGE_STUDENTS
   audience_category=AudienceCategory.WORKING_PROFESSIONALS
   audience_category=AudienceCategory.RESEARCHERS
   ```

4. **Finally: Test with Streamlit**
   ```bash
   streamlit run app.py
   ```

---

## Files Changed

| File | Change | Reason |
|------|--------|--------|
| `tools/curriculum_ingestion.py` | Added `ingest_from_folder()` method | To read .txt files from folder |
| `services/vector_store.py` | Fixed ChromaDB initialization | Was using deprecated API |
| `test_curriculum_loading.py` | **NEW** test script | Manual test for curriculum loading |

---

## Summary Table

| Aspect | Before | After |
|--------|--------|-------|
| Curriculum source | Only hardcoded examples | Reads from `data/sample_curricula/` + fallback to hardcoded |
| ChromaDB API | Deprecated `Settings()` | New `PersistentClient()` |
| Vector store status | Failed to initialize | ✅ Working |
| java.txt loading | Not loaded | ✅ Chunks 2 pieces, embeds, stores |
| Folder scanning | Not implemented | ✅ Auto-discovers .txt files |
| Manual test | N/A | ✅ `test_curriculum_loading.py` |

---

## Answer to Your Questions

**Q: "How will I test manually that it is reading content from data/sample_curriculum folder?"**

A: Run this:
```bash
python test_curriculum_loading.py
```

It will:
- ✅ Show "Found 1 .txt files in data/sample_curricula" (java.txt)
- ✅ Show "Loaded 2 chunks from folder"
- ✅ Run similarity searches
- ✅ Print retrieved content

**Q: "Is this what the update we have done?"**

A: Yes! We just added:
1. `ingest_from_folder()` method to scan the folder ← NEW
2. Fixed ChromaDB initialization error ← CRITICAL FIX
3. Created test script to verify it works ← VERIFICATION

The `java.txt` file exists but wasn't being used. Now it is!

