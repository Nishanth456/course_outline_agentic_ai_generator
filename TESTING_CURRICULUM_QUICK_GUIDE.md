# Manual Testing Quick Reference

## Single Command to Test Everything

```bash
python test_curriculum_loading.py
```

## What You Should See

### ✅ SUCCESS Output:
```
================================================================================
CURRICULUM LOADING TEST - Read from data/sample_curricula folder
================================================================================

📦 Step 1: Initializing services...
   ✅ Services initialized

📂 Step 2: Loading curriculum from data/sample_curricula...
   ✅ Loaded 2 chunks from folder
   ✅ Created 2 VectorDocuments

🔍 Step 3: Checking vector store...
   ✅ Vector store stats: {'collection_name': 'academic_knowledge', 
                           'document_count': 2, ...}

🔎 Step 4: Testing similarity search...
   Query: 'object oriented programming java'
   Found 2 results:
     1. [0.177] Java
        Object Oriented Programming with Java by Debasis Samanta...
     2. [-0.425] Java
        Class Process Class Runtime Class SecurityManager...

📋 Step 5: Checking metadata on retrieved documents...
   Document 1 metadata:
     - source_name: Java
     - source_type: syllabus
     - institution: Sample Curriculum Library
     - audience_level: beginner
   ✅ Metadata properly attached

================================================================================
✅ CURRICULUM LOADING TEST PASSED
================================================================================

Summary:
  ✅ Loaded 2 chunks from curriculum files
  ✅ Vector embeddings created and indexed
  ✅ Similarity search working
  ✅ Metadata preserved on all documents
```

## What This Proves

| Check | What It Verifies |
|-------|------------------|
| "Found 1 .txt files" | ✅ Folder scanning works |
| "Loaded 2 chunks" | ✅ File chunking works |
| "Created 2 VectorDocuments" | ✅ Metadata attachment works |
| "Vector store stats" | ✅ ChromaDB storage works |
| "Found 2 results" | ✅ Similarity search works |
| "source_name: Java" | ✅ Metadata preserved |
| "PASSED" | ✅ End-to-end working |

## What Each Step Does

### Step 1: Initialize Services
Loads the embedding service and resets the vector store

Expected: `✅ Services initialized`

### Step 2: Load Curriculum from Folder
Scans `data/sample_curricula/` for `.txt` files and ingests them

Expected: 
```
✅ Loaded 2 chunks from folder
✅ Created 2 VectorDocuments
```

This proves:
- ✅ `java.txt` was found
- ✅ Split into 2 chunks
- ✅ Each chunk got embeddings
- ✅ Stored in ChromaDB

### Step 3: Check Vector Store
Queries the database to verify documents were stored

Expected:
```
✅ Vector store stats: {'document_count': 2, ...}
```

### Step 4: Test Similarity Search
Runs 3 different queries against the stored documents

Expected: 
```
Query: 'object oriented programming java'
Found 2 results:
  1. [0.177] Java
  2. [-0.425] Java
```

The scores are similarity scores (higher = more relevant).

### Step 5: Verify Metadata
Checks that metadata is preserved on retrieved documents

Expected:
```
source_name: Java ✅
source_type: syllabus ✅
institution: Sample Curriculum Library ✅
audience_level: beginner ✅
```

## Troubleshooting

### ❌ "Failed to initialize VectorStore"
**Solution:** ChromaDB initialization failed
```bash
# Clear and retry
rm -rf chroma_db/
python test_curriculum_loading.py
```

### ❌ "No .txt files found in data/sample_curricula"
**Solution:** `java.txt` is missing
```bash
# Verify file exists
ls data/sample_curricula/
# Should show: java.txt (plus .gitkeep)
```

### ❌ "Search failed"
**Solution:** Vector store not initialized properly
```bash
# Reset and rerun
python -c "from services.vector_store import reset_vector_store; reset_vector_store()"
python test_curriculum_loading.py
```

## What Happens Inside

### File: `data/sample_curricula/java.txt`
```
Object Oriented Programming with Java
by Debasis Samanta
...
(368 lines of Java curriculum content)
```

### Processing:
```
Raw file (368 lines)
    ↓
Text cleaning (remove artifacts, normalize)
    ↓
Split into chunks (~500 words each)
    ↓
Create 2 VectorDocuments:
    Chunk 1: "Object Oriented Programming with Java..." (first 500 words)
    Chunk 2: "Class definitions, inheritance, polymorphism..." (next 500 words)
    ↓
Embed each chunk to 384-D vector
    ↓
Store with metadata:
    {
      "content": "...",
      "embedding": [0.1, -0.2, ..., 0.8],  // 384 numbers
      "metadata": {
        "source_name": "Java",
        "source_type": "syllabus",
        "institution_name": "Sample Curriculum Library",
        "audience_level": "beginner",
        "degree_level": "undergraduate"
      }
    }
    ↓
Stored in ChromaDB
```

## Adding More Curricula

Just add `.txt` files to `data/sample_curricula/`:

```bash
# Add Python curriculum
echo "Python fundamentals..." > data/sample_curricula/python.txt

# Add Database curriculum  
echo "SQL and database design..." > data/sample_curricula/databases.txt

# Next run will automatically load them
python test_curriculum_loading.py
# Will find 3 files instead of 1
```

## Integration with RetrievalAgent

When you use the full app:

```
User: "Create a Java course for beginners"
    ↓
RetrievalAgent searches vector store:
    - Searches for "java", "object oriented", "functions", etc.
    - Finds chunks from our loaded java.txt
    - Returns top 5 chunks with similarity scores
    ↓
ModuleCreationAgent receives retrieved chunks:
    - Uses them as reference material
    - Incorporates into course outline
    - Better, more grounded content
```

## Files Involved

```
data/sample_curricula/
├── java.txt              ← Your curriculum file
└── .gitkeep

tools/
├── curriculum_ingestion.py
│   ├── ingest_from_folder()         ← Main method (NEW)
│   ├── ingest_text()                ← Helper
│   └── ingest_example_curriculum()  ← Fallback

services/
├── vector_store.py
│   ├── initialize()                 ← Fixed ChromaDB API
│   ├── add_documents()
│   └── similarity_search()

tests/
└── test_curriculum_loading.py       ← This test!
```

## Success Checklist

Before moving to next steps, verify:

- [ ] Run: `python test_curriculum_loading.py`
- [ ] See: `✅ CURRICULUM LOADING TEST PASSED`
- [ ] Check: Output shows 2 chunks loaded
- [ ] Check: Similarity search shows results
- [ ] Check: Metadata is preserved

Then you're ready for:
```bash
pytest tests/test_phase_3_retrieval.py -v  # Run full test suite
streamlit run app.py                        # Test in app
```

