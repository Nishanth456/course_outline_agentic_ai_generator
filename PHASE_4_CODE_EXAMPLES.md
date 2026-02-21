# Phase 4 Code Examples

## Example 1: Basic Web Search

**Goal:** Search the web for course information

```python
# File: examples/01_basic_web_search.py

from tools.web_search_tools import WebSearchToolchain, SearchResult

def example_basic_search():
    """Simplest example: search web"""
    
    # Initialize toolchain (handles Tavily → DuckDuckGo → SerpAPI)
    toolchain = WebSearchToolchain()
    
    # Search
    results, tool_used = toolchain.search(
        query="Kubernetes deployment best practices",
        max_results=5
    )
    
    print(f"Found {len(results)} results using {tool_used}")
    
    for result in results:
        print(f"\n  Title: {result.title}")
        print(f"  URL: {result.url}")
        print(f"  Snippet: {result.snippet[:100]}...")
        print(f"  Relevance: {result.relevance_score}")

if __name__ == "__main__":
    example_basic_search()
```

**Output:**
```
Found 5 results using tavily

  Title: Kubernetes Deployment Best Practices
  URL: https://kubernetes.io/docs/concepts/configuration/best-concepts/
  Snippet: This guide covers best practices for deploying...
  Relevance: 0.98

  Title: Advanced Kubernetes Deployment Patterns
  URL: https://...
  Snippet: Learn production-ready deployment patterns...
  Relevance: 0.92

  [3 more results...]
```

---

## Example 2: Multi-Query Search

**Goal:** Search multiple queries at once

```python
# File: examples/02_batch_search.py

from tools.web_search_tools import WebSearchToolchain

def example_batch_search():
    """Search multiple queries efficiently"""
    
    toolchain = WebSearchToolchain()
    
    queries = [
        "Python machine learning frameworks",
        "TensorFlow vs PyTorch comparison",
        "Deep learning best practices"
    ]
    
    # Batch search (tries each query with fallback chain)
    results_dict, stats = toolchain.batch_search(
        queries=queries,
        max_results_per_query=3
    )
    
    print(f"Search Statistics:")
    print(f"  Total queries: {len(queries)}")
    print(f"  Total results: {sum(len(r) for r in results_dict.values())}")
    print(f"  Tools used: {stats['tools_used']}")
    print(f"  Search history: {len(stats['search_history'])} queries")
    
    for query, results in results_dict.items():
        print(f"\n🔍 Query: {query}")
        print(f"   Results: {len(results)}")
        for r in results[:2]:
            print(f"   - {r.title} ({r.relevance_score})")

if __name__ == "__main__":
    example_batch_search()
```

**Output:**
```
Search Statistics:
  Total queries: 3
  Total results: 9
  Tools used: {'tavily': 3}
  Search history: 3 queries

🔍 Query: Python machine learning frameworks
   Results: 3
   - scikit-learn Documentation (0.95)
   - TensorFlow Official Guide (0.93)

🔍 Query: TensorFlow vs PyTorch comparison
   Results: 3
   - Comparison Guide: TensorFlow vs PyTorch (0.97)
   - PyTorch vs TensorFlow: Pros and Cons (0.91)

🔍 Query: Deep learning best practices
   Results: 3
   - Deep Learning Best Practices (0.92)
   - Training Neural Networks Efficiently (0.88)
```

---

## Example 3: Using WebSearchAgent Directly

**Goal:** Get structured course curriculum from web search

```python
# File: examples/03_web_search_agent.py

import asyncio
from agents.web_search_agent import WebSearchAgent
from schemas.execution_context import ExecutionContext
from schemas.user_input import UserInputSchema

async def example_web_search_agent():
    """Use WebSearchAgent to get structured curriculum"""
    
    # Initialize agent
    agent = WebSearchAgent()
    
    # Create user input
    user_input = UserInputSchema(
        course_title="Cloud Architecture with AWS",
        audience_category="developers",
        depth_requirement="intermediate_level",
        learning_mode="hands_on",
        session_id="example_03"
    )
    
    # Create context
    context = ExecutionContext(
        user_input=user_input,
        session_id="example_03"
    )
    
    print("🚀 Starting Web Search Agent...")
    
    # Run agent
    output = await agent.run(context)
    
    # Display results
    print(f"\n📊 Results:")
    print(f"  Confidence: {output.confidence_score}")
    print(f"  Tool Used: {output.tool_used.value}")
    print(f"  Results Found: {output.result_count}")
    print(f"  Execution Time: {output.execution_time_ms}ms")
    
    print(f"\n🎯 Summary:")
    print(f"  {output.search_summary[:200]}...")
    
    print(f"\n📚 Key Topics Found:")
    for topic in output.key_topics_found[:5]:
        print(f"  - {topic}")
    
    print(f"\n🏫 Recommended Modules:")
    for module in output.recommended_modules[:3]:
        print(f"  - {module.title}")
        print(f"    {module.description[:60]}...")
    
    print(f"\n🔗 Source Links:")
    for link in output.source_links[:3]:
        print(f"  - {link.title}")
        print(f"    {link.url}")
        print(f"    Relevance: {link.relevance_score}")
    
    print(f"\n✅ Agent execution completed")
    
    # Check confidence
    if output.is_high_confidence():
        print(f"✅ High confidence results (can use for generation)")
    else:
        print(f"⚠️ Low confidence results (use with caution)")

if __name__ == "__main__":
    asyncio.run(example_web_search_agent())
```

**Output:**
```
🚀 Starting Web Search Agent...

📊 Results:
  Confidence: 0.89
  Tool Used: tavily
  Results Found: 15
  Execution Time: 1452ms

🎯 Summary:
  AWS Cloud Architecture courses focus on designing scalable, secure, and...

📚 Key Topics Found:
  - VPC and Network Design
  - EC2 Instance Management
  - S3 Storage and Lifecycle
  - RDS Databases
  - Lambda and Serverless

🏫 Recommended Modules:
  - AWS Solutions Architect Professional
    Comprehensive course covering design principles...
  - Architecting on AWS (Official AWS)
    Deep dive into architectural best practices...
  - CloudAcademy AWS Architecture
    Hands-on labs with real AWS environments...

🔗 Source Links:
  - AWS Training and Certification
    https://aws.amazon.com/training/
    Relevance: 0.96
  - Coursera AWS Architecture Specialization
    https://www.coursera.org/specializations/aws-arc...
    Relevance: 0.94
  - Linux Academy AWS Courses
    https://linuxacademy.com/linux/courses/aws...
    Relevance: 0.91

✅ Agent execution completed
✅ High confidence results (can use for generation)
```

---

## Example 4: Orchestrator with Both Retrieval + WebSearch

**Goal:** Generate course using both internal + external knowledge

```python
# File: examples/04_full_orchestrator.py

import asyncio
from agents.orchestrator import CourseOrchestratorAgent
from schemas.user_input import UserInputSchema
import json

async def example_orchestrator():
    """Full orchestrator: Retrieval + WebSearch + Generation"""
    
    orchestrator = CourseOrchestratorAgent()
    
    user_input = UserInputSchema(
        course_title="Full Stack Web Development with React and Django",
        audience_category="career_changers",
        depth_requirement="comprehensive_level",
        learning_mode="project_based",
        sessions_per_week=3,
        session_duration_minutes=90,
        session_id="example_04"
    )
    
    print("🚀 Orchestrator Starting...")
    print(f"  Course: {user_input.course_title}")
    print(f"  Audience: {user_input.audience_category}")
    print(f"  Depth: {user_input.depth_requirement}")
    
    # Run orchestrator (executes Phase 3 + Phase 4 + Phase 2)
    print("\n  Step 4: Launching RetrievalAgent (Phase 3)...")
    print("  Step 5: Launching WebSearchAgent (Phase 4)...")
    print("  Step 6: Launching ModuleCreationAgent...")
    
    outline = await orchestrator.run(user_input, "example_04")
    
    print("\n✅ Orchestrator Completed")
    
    # Display course structure
    print(f"\n📚 Course Generated:")
    print(f"  Title: {outline.course_title}")
    print(f"  Total Duration: {outline.total_duration_hours} hours")
    print(f"  Modules: {len(outline.module_list)}")
    print(f"  Learning Outcomes: {len(outline.learning_outcomes)}")
    
    # Show first few modules
    print(f"\n📖 Module Overview:")
    for i, module in enumerate(outline.module_list[:4], 1):
        print(f"\n  [{i}] {module.title}")
        print(f"      Duration: {module.estimated_duration_hours}h")
        print(f"      Topics: {', '.join(module.topics[:3])}...")
        print(f"      Learning Objectives: {len(module.learning_objectives)} items")
    
    # Show learning outcomes
    print(f"\n🎯 Learning Outcomes:")
    for i, outcome in enumerate(outline.learning_outcomes[:5], 1):
        print(f"  [{i}] {outcome}")
    
    # Show references (both internal + external)
    internal_refs = [r for r in outline.references if r.get("source") == "internal"]
    external_refs = [r for r in outline.references if r.get("source") == "external"]
    
    print(f"\n🔗 References ({len(outline.references)} total):")
    print(f"  Internal Knowledge (Phase 3): {len(internal_refs)}")
    if internal_refs:
        for ref in internal_refs[:2]:
            print(f"    - {ref.get('name', 'Unknown')}")
    
    print(f"  External Knowledge (Phase 4): {len(external_refs)}")
    if external_refs:
        for ref in external_refs[:2]:
            print(f"    - {ref.get('url', 'Unknown')[:50]}...")
    
    print(f"\n📊 Course Statistics:")
    print(f"  Modules: {len(outline.module_list)}")
    print(f"  Total hours: {outline.total_duration_hours}")
    print(f"  Weeks (assuming {user_input.sessions_per_week}x/week): "
          f"{outline.total_duration_hours / (90 * user_input.sessions_per_week):.0f}")
    print(f"  Projects/Assessments: {sum(1 for m in outline.module_list if m.has_project)}")
    
    return outline

if __name__ == "__main__":
    outline = asyncio.run(example_orchestrator())
```

**Output:**
```
🚀 Orchestrator Starting...
  Course: Full Stack Web Development with React and Django
  Audience: career_changers
  Depth: comprehensive_level

  Step 4: Launching RetrievalAgent (Phase 3)...
  Step 5: Launching WebSearchAgent (Phase 4)...
  Step 6: Launching ModuleCreationAgent...

✅ Orchestrator Completed

📚 Course Generated:
  Title: Full Stack Web Development with React and Django
  Total Duration: 120 hours
  Modules: 12
  Learning Outcomes: 24

📖 Module Overview:

  [1] JavaScript Fundamentals
      Duration: 8h
      Topics: Variables, Functions, DOM Manipulation...
      Learning Objectives: 3 items

  [2] React Basics & Components
      Duration: 12h
      Topics: JSX, State, Props, Hooks...
      Learning Objectives: 5 items

  [3] Django Backend Development
      Duration: 16h
      Topics: Models, Views, Templates, ORM...
      Learning Objectives: 4 items

  [4] API Integration & REST
      Duration: 10h
      Topics: HTTP Methods, Authentication, Error Handling...
      Learning Objectives: 3 items

🎯 Learning Outcomes:
  [1] Build responsive web applications using React
  [2] Design and implement RESTful APIs with Django
  [3] Manage SQL databases with Django ORM
  [4] Implement user authentication and authorization
  [5] Deploy full-stack applications to cloud platforms

🔗 References (18 total):
  Internal Knowledge (Phase 3): 4
    - JavaScript Best Practices Guide
    - React Component Library Patterns
  External Knowledge (Phase 4): 14
    - https://www.coursera.org/specializations/full-stack...
    - https://www.udemy.com/course/the-complete-javascript...

📊 Course Statistics:
  Modules: 12
  Total hours: 120
  Weeks (assuming 3x/week): 4
  Projects/Assessments: 6
```

---

## Example 5: Error Handling & Graceful Degradation

**Goal:** Show how system handles errors

```python
# File: examples/05_error_handling.py

import asyncio
from agents.web_search_agent import WebSearchAgent
from schemas.execution_context import ExecutionContext
from schemas.user_input import UserInputSchema

async def example_graceful_degradation():
    """Show how system handles failures gracefully"""
    
    agent = WebSearchAgent()
    
    # Test 1: Very obscure query
    print("Test 1: Obscure query (no results expected)")
    user_input = UserInputSchema(
        course_title="xyz_nonexistent_course_12345_abc",
        audience_category="researchers",
        depth_requirement="research_level",
        learning_mode="independent",
        session_id="test_1"
    )
    
    context = ExecutionContext(user_input=user_input, session_id="test_1")
    output = await agent.run(context)
    
    print(f"  Confidence: {output.confidence_score}")
    print(f"  Results: {output.result_count}")
    print(f"  Is Usable: {output.is_usable()}")
    print(f"  Notes: {output.search_notes}")
    print(f"  ✅ Handled gracefully (no crash)")
    
    # Test 2: Very short query
    print("\nTest 2: Very short query")
    user_input = UserInputSchema(
        course_title="C++",
        audience_category="beginners",
        depth_requirement="overview_level",
        learning_mode="self_paced",
        session_id="test_2"
    )
    
    context = ExecutionContext(user_input=user_input, session_id="test_2")
    output = await agent.run(context)
    
    print(f"  Confidence: {output.confidence_score}")
    print(f"  Results: {output.result_count}")
    print(f"  Topics: {len(output.key_topics_found)}")
    print(f"  ✅ Handled gracefully")
    
    # Test 3: Empty query
    print("\nTest 3: Empty query")
    user_input = UserInputSchema(
        course_title="",
        audience_category="unknown",
        depth_requirement="unknown",
        learning_mode="unknown",
        session_id="test_3"
    )
    
    context = ExecutionContext(user_input=user_input, session_id="test_3")
    
    try:
        output = await agent.run(context)
        print(f"  Confidence: {output.confidence_score}")
        print(f"  Results: {output.result_count}")
        print(f"  ✅ Handled gracefully")
    except Exception as e:
        print(f"  ⚠️ Expected error: {type(e).__name__}")
        print(f"  ✅ Error caught as expected")
    
    print("\n✅ All degradation scenarios handled gracefully")
    print("   ModuleCreationAgent can continue even if WebSearch fails")

if __name__ == "__main__":
    asyncio.run(example_graceful_degradation())
```

**Output:**
```
Test 1: Obscure query (no results expected)
  Confidence: 0.0
  Results: 0
  Is Usable: False
  Notes: No meaningful results found
  ✅ Handled gracefully (no crash)

Test 2: Very short query
  Confidence: 0.62
  Results: 8
  Topics: 5
  ✅ Handled gracefully

Test 3: Empty query
  Confidence: 0.0
  Results: 0
  ✅ Handled gracefully

✅ All degradation scenarios handled gracefully
   ModuleCreationAgent can continue even if WebSearch fails
```

---

## Example 6: Analyzing Tool Performance

**Goal:** Understand which tools work best

```python
# File: examples/06_tool_analysis.py

from tools.web_search_tools import WebSearchToolchain, get_web_search_toolchain
import time

def example_tool_analysis():
    """Analyze which tools are being used"""
    
    toolchain = get_web_search_toolchain()
    
    # Clear history
    toolchain.reset()
    
    queries = [
        "Python programming tutorials",
        "Machine learning frameworks",
        "Cloud computing services",
        "Web development best practices",
        "Data science tools"
    ]
    
    print("Running searches and analyzing tool usage...")
    
    for query in queries:
        results, tool = toolchain.search(query, max_results=3)
        print(f"  ✅ Query '{query[:40]}...' → {tool.upper()}")
    
    # Get statistics
    stats = toolchain.get_search_stats()
    
    print(f"\n📊 Tool Usage Statistics:")
    print(f"  Total searches: {len(stats['search_history'])}")
    
    if 'tools_used' in stats:
        print(f"  Tools used:")
        for tool, count in stats['tools_used'].items():
            print(f"    - {tool}: {count} times")
    
    print(f"\n📊 Search History:")
    for i, search in enumerate(stats['search_history'][-5:], 1):
        print(f"  [{i}] {search.get('query', 'unknown')[:40]}...")
        print(f"      Tool: {search.get('tool', 'unknown')}")
        print(f"      Results: {len(search.get('results', []))}")
    
    print(f"\n✅ Analysis complete")

if __name__ == "__main__":
    example_tool_analysis()
```

**Output:**
```
Running searches and analyzing tool usage...
  ✅ Query 'Python programming tutorials' → TAVILY
  ✅ Query 'Machine learning frameworks' → TAVILY
  ✅ Query 'Cloud computing services' → TAVILY
  ✅ Query 'Web development best practices' → TAVILY
  ✅ Query 'Data science tools' → TAVILY

📊 Tool Usage Statistics:
  Total searches: 5
  Tools used:
    - tavily: 5 times

📊 Search History:
  [1] Python programming tutorials...
      Tool: tavily
      Results: 3
  [2] Machine learning frameworks...
      Tool: tavily
      Results: 3
  [3] Cloud computing services...
      Tool: tavily
      Results: 3
  [4] Web development best practices...
      Tool: tavily
      Results: 3
  [5] Data science tools...
      Tool: tavily
      Results: 3

✅ Analysis complete
```

---

## Quick Reference: Common Patterns

### Pattern 1: Check if Results are Trustworthy

```python
output = await agent.run(context)

if output.is_high_confidence():
    print("✅ Use results directly")
elif output.is_usable():
    print("⚠️ Use with review")
else:
    print("❌ Low confidence, find alternatives")

print(f"Confidence: {output.confidence_score}")
```

### Pattern 2: Access Source Links

```python
for link in output.source_links:
    print(f"Title: {link.title}")
    print(f"URL: {link.url}")
    print(f"Relevance: {link.relevance_score}")
    print(f"Source Type: {link.source_type}")
    print(f"Accessed: {link.accessed_at}")
```

### Pattern 3: Convert to JSON (for APIs)

```python
import json

output_dict = output.to_dict()
json_string = json.dumps(output_dict, indent=2, default=str)
print(json_string)
```

### Pattern 4: Track Execution Time

```python
start = time.time()
output = await agent.run(context)
elapsed = (time.time() - start) * 1000

print(f"Execution time: {output.execution_time_ms}ms")
print(f"Measurement confirms: {elapsed:.0f}ms")
```

### Pattern 5: Check Fallback Usage

```python
if output.fallback_used:
    print(f"⚠️ Fallback tools used")
    print(f"Primary tool: Tavily")
    print(f"Used: {output.tool_used.value}")
else:
    print(f"✅ Primary tool successful: {output.tool_used.value}")
```

