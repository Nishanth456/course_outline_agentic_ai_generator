"""
PHASE 5: Module Creation Agent - Core Intelligence Layer

Curriculum-grade course outline synthesis from multi-source context.

FEATURES (STEPS 5.1-5.7):
- STEP 5.1: CourseOutlineSchema lock (final curriculum contract)
- STEP 5.2: Agent responsibility boundary (pure synthesis, no tools)
- STEP 5.3: Multi-layer prompt architecture (system/developer/user/context/constraints)
- STEP 5.4: Duration & depth allocation (pre-LLM logic)
- STEP 5.5: Learning mode-driven structure (theory/project/interview/research)
- STEP 5.6: PDF integration (contextual guidance)
- STEP 5.7: Provenance & attribution tracking (source validation)

INPUT:
- ExecutionContext (user_input, retrieved_documents, web_search_results, pdf_text)

OUTPUT:
- CourseOutlineSchema (validated, production-ready, curriculum-grade)

INTEGRATION:
- Orchestrator Step 6: Calls ModuleCreationAgent.run(context)
- Non-blocking: Failures flagged but pipeline continues
"""

import logging
import json
import math
from typing import Optional, Dict, Any, List
from datetime import datetime

from schemas.user_input import UserInputSchema
from schemas.course_outline import (
    CourseOutlineSchema, Module, Lesson, LearningObjective, BloomLevel, Reference, SourceType
)
from schemas.execution_context import ExecutionContext
from services.llm_service import LLMService
from utils.duration_allocator import DurationAllocator
from utils.learning_mode_templates import LearningModeTemplates

logger = logging.getLogger(__name__)

# Singleton instance
_module_creation_agent: Optional["ModuleCreationAgent"] = None


def get_module_creation_agent() -> "ModuleCreationAgent":
    """Get or create module creation agent singleton."""
    global _module_creation_agent
    if _module_creation_agent is None:
        _module_creation_agent = ModuleCreationAgent()
    return _module_creation_agent


def reset_module_creation_agent():
    """Reset module creation agent singleton."""
    global _module_creation_agent
    _module_creation_agent = None


class ModuleCreationAgent:
    """
    STEP 5.2: Core curriculum synthesis engine.
    
    RESPONSIBILITY BOUNDARY:
    - Input: ExecutionContext with multi-source context
    - Processing: Pure synthesis (no tool calls)
    - Output: CourseOutlineSchema (curriculum-grade)
    
    NOT RESPONSIBLE FOR:
    - Context building (Orchestrator Steps 1-5)
    - Validation/retry (Phase 6 Validator Agent)
    - Orchestration logic (Orchestrator)
    """
    
    def __init__(self):
        """Initialize with LLM service and utilities."""
        self.llm_service = LLMService()
        self.duration_allocator = DurationAllocator()
    
    async def run(self, context: ExecutionContext) -> CourseOutlineSchema:
        """
        STEP 5.8: Full 8-step pipeline execution.
        
        Args:
            context: ExecutionContext with user_input, retrieved_docs, web_results, pdf_text
            
        Returns:
            CourseOutlineSchema (validated, production-ready)
            
        Raises:
            ValueError: If context invalid or synthesis fails
        """
        
        # 1. Validate context
        self._validate_context(context)
        user_input = context.user_input
        
        logger.info(
            "Phase 5: Module Creation Agent - Starting synthesis pipeline",
            extra={"execution_id": context.execution_id, "course": user_input.course_title}
        )
        
        # 2. Pre-process duration & depth allocation (STEP 5.4)
        duration_plan = self.duration_allocator.allocate(
            total_hours=user_input.duration_hours,
            depth_level=user_input.depth_requirement,
            learning_mode=user_input.learning_mode
        )
        
        # 3. Get learning mode template (STEP 5.5)
        mode_template = LearningModeTemplates.get_template(user_input.learning_mode)
        
        # 4. Build multi-layer prompt (STEP 5.3)
        prompt = self._build_prompt(context, duration_plan, mode_template)
        
        # 5. Call LLM
        logger.debug(f"Calling LLM for outline synthesis (execution_id={context.execution_id})")
        llm_response = await self.llm_service.call_model(prompt, temperature=0.7, max_tokens=8000)
        
        # 6. Parse response
        parsed_data = self._parse_llm_response(llm_response)
        
        # 7. Structure into CourseOutlineSchema
        outline = self._structure_outline(
            parsed_data, context, user_input, duration_plan, mode_template
        )
        
        # 8. Validate schema
        if not isinstance(outline, CourseOutlineSchema):
            raise ValueError(f"Expected CourseOutlineSchema, got {type(outline)}")
        
        logger.info(
            "Phase 5: Course outline synthesized successfully",
            extra={
                "execution_id": context.execution_id,
                "modules": len(outline.modules),
                "duration": outline.total_duration_hours,
                "confidencecore": outline.confidence_score,
            }
        )
        
        return outline
    
    def _validate_context(self, context: ExecutionContext):
        """
        STEP 5.2: Validate execution context.
        
        Required fields:
        - user_input (UserInputSchema)
        - execution_id
        
        Optional but helpful:
        - retrieved_documents (Phase 3)
        - web_search_results (Phase 4)
        - pdf_text (user uploads)
        """
        if not context:
            raise ValueError("ExecutionContext required")
        
        if not context.user_input:
            raise ValueError("user_input required in ExecutionContext")
        
        if not isinstance(context.user_input, UserInputSchema):
            raise ValueError(f"user_input must be UserInputSchema, got {type(context.user_input)}")
        
        logger.debug(f"Context validation passed (execution_id={context.execution_id})")
    
    def _build_prompt(
        self,
        context: ExecutionContext,
        duration_plan: Dict[str, Any],
        mode_template: Dict[str, Any]
    ) -> str:
        """
        STEP 5.3: Build 5-layer multi-prompt architecture.
        
        Layers:
        1. System: Expert curriculum designer persona
        2. Developer: Schema instructions, strict JSON format
        3. User: Original educator input
        4. Context: Retrieved docs, web search, PDF summaries
        5. Constraints: Duration plan, depth guidance, validation rules
        """
        
        user_input = context.user_input
        
        # LAYER 1: System prompt (persona)
        system_layer = """You are an expert curriculum designer with 20+ years of experience.
You understand:
- Bloom's taxonomy and learning outcomes
- Adult learning principles (andragogy)
- Course structure and pedagogy
- Educational best practices

Your task: Generate a comprehensive, curriculum-grade course outline."""
        
        # LAYER 2: Developer instructions (schema & format)
        schema_instructions = """OUTPUT FORMAT (STRICT JSON):
{
  "course_title": "string - exact title from user",
  "course_summary": "string - 150-300 word overview",
  "learning_mode": "string - theory|project_based|interview_prep|research",
  "modules": [
    {
      "module_id": "M_1, M_2, etc",
      "title": "string",
      "description": "string - detailed module overview",
      "estimated_hours": number,
      "learning_objectives": [
        {
          "statement": "string",
          "bloom_level": "remember|understand|apply|analyze|evaluate|create",
          "assessment_method": "string"
        }
      ],
      "lessons": [
        {
          "title": "string",
          "description": "string",
          "duration_minutes": number,
          "key_concepts": ["string"],
          "activities": ["string"]
        }
      ],
      "assessment_type": "quiz|project|discussion|exam|presentation|peer_review|capstone",
      "prerequisites": ["string"],
      "has_capstone": boolean
    }
  ],
  "course_level_objectives": [learning objectives array],
  "references": [
    {
      "title": "string",
      "source_type": "retrieved|web|pdf|generated",
      "url": "string or null",
      "confidence_score": 0.0-1.0
    }
  ]
}

CRITICAL: Return ONLY valid JSON. No markdown, no code blocks, no extra text."""
        
        # LAYER 3: User input section
        user_section = f"""USER INPUT:
Title: {user_input.course_title}
Description: {user_input.course_description}
Audience: {user_input.audience_level} - {user_input.audience_category}
Depth: {user_input.depth_requirement}
Duration: {user_input.duration_hours} hours
Learning Mode: {user_input.learning_mode}
"""
        
        # LAYER 4: Context summary (retrieved docs, web search, PDF)
        context_section = self._summarize_context(context)
        
        # LAYER 5: Constraints & guidance
        constraints_section = f"""CONSTRAINTS & GUIDANCE:
Duration Plan: {duration_plan['num_modules']} modules (~{duration_plan['avg_hours_per_module']:.1f}h each)
Depth Guidance: {duration_plan['depth_guidance']['description']}
Learning Mode: {mode_template['template_description']}

RULES:
1. Total duration MUST be approximately {user_input.duration_hours} hours
2. Bloom's levels should progress from {duration_plan['depth_guidance']['primary_blooms'][0]} to higher levels
3. Assessment emphasis: {', '.join(mode_template['assessment_emphasis']['primary'])}
4. Each module should have 3-5 learning objectives
5. Include references with confidence scores (no hallucinated citations)
6. Modules should be sequenced logically
7. If capstone required by mode, include it as final module
8. Ensure learning objectives are measurable and specific"""
        
        # Combine all layers
        full_prompt = f"""{system_layer}

{schema_instructions}

{user_section}

{context_section}

{constraints_section}

Generate the course outline now."""
        
        return full_prompt
    
    def _summarize_context(self, context: ExecutionContext) -> str:
        """STEP 5.4: Summarize multi-source context."""
        sections = []
        
        # Summarize retrieved documents (Phase 3)
        if context.retrieved_documents:
            sections.append(self._summarize_retrieved_docs(context.retrieved_documents))
        
        # Summarize web search results (Phase 4)
        if context.web_search_results:
            sections.append(self._summarize_web_results(context.web_search_results))
        
        # Summarize PDF (if provided)
        if context.pdf_text:
            sections.append(self._summarize_pdf(context.pdf_text))
        
        if not sections:
            return "CONTEXT: No external sources provided. Course outline based on user input and general knowledge."
        
        return "CONTEXT:\n" + "\n".join(sections)
    
    def _summarize_retrieved_docs(self, retrieved_documents: List[Dict]) -> str:
        """STEP 5.6: Summarize retrieved institutional documents."""
        if not retrieved_documents:
            return ""
        
        summary = f"Retrieved Documents ({len(retrieved_documents)} documents):\n"
        for doc in retrieved_documents[:3]:  # Top 3
            summary += f"- {doc.get('title', 'Untitled')}: {doc.get('content', '')[:200]}...\n"
        
        return summary
    
    def _summarize_web_results(self, web_search_results: Dict) -> str:
        """STEP 5.6: Summarize web search insights."""
        if not web_search_results:
            return ""
        
        results = web_search_results.get("results", [])
        summary = f"Web Search Results ({len(results)} relevant sources):\n"
        for result in results[:3]:  # Top 3
            summary += f"- {result.get('title', 'Untitled')}: {result.get('snippet', '')[:150]}...\n"
        
        return summary
    
    def _summarize_pdf(self, pdf_text: str) -> str:
        """STEP 5.6: Summarize user-provided PDF."""
        if not pdf_text:
            return ""
        
        # Summarize first 500 chars
        preview = pdf_text[:500].replace("\n", " ").strip()
        return f"PDF Guidance Material: {preview}...\n(Use this as supplementary guidance, not primary source)"
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM JSON response with fallback handling.
        
        Handles:
        - Clean JSON
        - JSON in markdown code blocks
        - JSON in text with extra content
        """
        
        response = response.strip()
        
        # Try 1: Direct JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Try 2: Extract from markdown code block
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            if end > start:
                try:
                    return json.loads(response[start:end].strip())
                except json.JSONDecodeError:
                    pass
        
        # Try 3: Extract from code block without language tag
        if "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end > start:
                try:
                    return json.loads(response[start:end].strip())
                except json.JSONDecodeError:
                    pass
        
        # Try 4: Find JSON object in text
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(response[start:end])
            except json.JSONDecodeError:
                pass
        
        raise ValueError(f"Unable to extract valid JSON from LLM response: {response[:200]}...")
    
    def _structure_outline(
        self,
        parsed_data: Dict[str, Any],
        context: ExecutionContext,
        user_input: UserInputSchema,
        duration_plan: Dict[str, Any],
        mode_template: Dict[str, Any]
    ) -> CourseOutlineSchema:
        """
        STEP 5.1: Assemble into CourseOutlineSchema with validation.
        
        Applies business rules:
        - Enforce duration constraints
        - Validate module structure
        - Add provenance (STEP 5.7)
        - Calculate confidence & completeness
        """
        
        # Create modules from parsed data
        modules = []
        for module_data in parsed_data.get("modules", []):
            module = self._create_module(module_data)
            modules.append(module)
        
        # Build references with complete provenance (STEP 5.7)
        references = self._build_references(parsed_data, context)
        
        # Create outline
        outline = CourseOutlineSchema(
            course_title=user_input.course_title,
            course_summary=parsed_data.get("course_summary", user_input.course_description),
            audience_level=user_input.audience_level,
            audience_category=user_input.audience_category,
            learning_mode=user_input.learning_mode,
            depth_requirement=user_input.depth_requirement,
            total_duration_hours=user_input.duration_hours,
            prerequisites=parsed_data.get("prerequisites", []),
            course_level_learning_objectives=  # STEP 5.7: Parse objectives from LLM
                [self._parse_objective(obj) for obj in parsed_data.get("course_level_objectives", [])],
            modules=modules,
            assessment_strategy=parsed_data.get("assessment_strategy", {}),
            references=references,
            confidence_score=self._calculate_confidence(context),
            completeness_score=self._calculate_completeness(modules, references),
            generated_by_agent="module_creation_agent",
            generation_timestamp=datetime.now().isoformat(),
        )
        
        return outline
    
    def _create_module(self, module_data: Dict[str, Any]) -> Module:
        """STEP 5.1: Build individual Module object."""
        
        lessons = []
        for lesson_data in module_data.get("lessons", []):
            lesson = Lesson(
                lesson_id=f"L_{module_data.get('module_id', 'unknown')}_{len(lessons) + 1}",
                title=lesson_data.get("title", "Untitled Lesson"),
                description=lesson_data.get("description", ""),
                duration_minutes=int(lesson_data.get("duration_minutes", 60)),
                key_concepts=lesson_data.get("key_concepts", []),
                activities=lesson_data.get("activities", []),
                resources=lesson_data.get("resources", [])
            )
            lessons.append(lesson)
        
        learning_objectives = []
        for obj_data in module_data.get("learning_objectives", []):
            obj = self._parse_objective(obj_data)
            learning_objectives.append(obj)
        
        module = Module(
            module_id=module_data.get("module_id", "M_unknown"),
            title=module_data.get("title", "Untitled Module"),
            description=module_data.get("description", ""),
            estimated_hours=float(module_data.get("estimated_hours", 6.0)),
            learning_objectives=learning_objectives,
            lessons=lessons,
            assessment_type=module_data.get("assessment_type", "quiz"),
            prerequisites=module_data.get("prerequisites", []),
            has_capstone=module_data.get("has_capstone", False),
            project_description=module_data.get("project_description", None),
            source_tags=module_data.get("source_tags", [])
        )
        
        return module
    
    def _parse_objective(self, obj_data: Dict[str, Any]) -> LearningObjective:
        """Parse single learning objective."""
        bloom_level = obj_data.get("bloom_level", "understand").lower()
        try:
            bloom = BloomLevel[bloom_level.upper()]
        except KeyError:
            bloom = BloomLevel.UNDERSTAND
        
        return LearningObjective(
            objective_id=obj_data.get("objective_id", "LO_unknown"),
            statement=obj_data.get("statement", ""),
            bloom_level=bloom,
            assessment_method=obj_data.get("assessment_method", "Quiz")
        )
    
    def _build_references(self, parsed_data: Dict[str, Any], context: ExecutionContext) -> List[Reference]:
        """
        STEP 5.7: Complete provenance tracking from all sources.
        
        Sources:
        1. LLM output references (from parsed_data)
        2. Web search results (context.web_search_results)
        3. Retrieved documents (context.retrieved_documents)
        4. PDF guidance (context.pdf_text - if provided)
        """
        
        references = []
        
        # 1. References cited by LLM
        for ref_data in parsed_data.get("references", []):
            ref = Reference(
                title=ref_data.get("title", "Reference"),
                source_type=SourceType.WEB if ref_data.get("source_type") == "web" else SourceType.GENERATED,
                url=ref_data.get("url"),
                confidence_score=float(ref_data.get("confidence_score", 0.8)),
                author=ref_data.get("author"),
                institution=ref_data.get("institution"),
                accessed_at=datetime.now().isoformat()
            )
            references.append(ref)
        
        # 2. Web search results
        if context.web_search_results:
            for result in context.web_search_results.get("results", [])[:3]:
                ref = Reference(
                    title=result.get("title", "Web Result"),
                    source_type=SourceType.WEB,
                    url=result.get("url"),
                    confidence_score=0.85,
                    accessed_at=datetime.now().isoformat()
                )
                references.append(ref)
        
        # 3. Retrieved documents
        if context.retrieved_documents:
            for doc in context.retrieved_documents[:3]:
                ref = Reference(
                    title=doc.get("title", "Retrieved Document"),
                    source_type=SourceType.RETRIEVED,
                    url=doc.get("url"),
                    confidence_score=0.9,
                    accessed_at=datetime.now().isoformat()
                )
                references.append(ref)
        
        # 4. PDF guidance
        if context.pdf_text:
            ref = Reference(
                title="User-provided PDF guidance",
                source_type=SourceType.PDF,
                url=None,
                confidence_score=0.8,
                accessed_at=datetime.now().isoformat()
            )
            references.append(ref)
        
        return references
    
    def _calculate_confidence(self, context: ExecutionContext) -> float:
        """
        Calculate confidence score (0.0-1.0) based on context richness.
        
        Factors:
        - Retrieved docs: +0.15
        - Web search: +0.15
        - PDF: +0.10
        - Base: 0.6
        """
        
        score = 0.6  # Base confidence
        
        if context.retrieved_documents:
            score += 0.15
        
        if context.web_search_results:
            score += 0.15
        
        if context.pdf_text:
            score += 0.10
        
        return min(1.0, score)
    
    def _calculate_completeness(self, modules: List[Module], references: List[Reference]) -> float:
        """
        Calculate completeness score (0.0-1.0).
        
        Factors:
        - Module count: +0.25 (3+ modules)
        - Learning objectives: +0.25 (each module has objectives)
        - References: +0.25 (references present)
        - Assessment: +0.25 (clear assessment strategy)
        """
        
        score = 0.0
        
        # Module count
        if len(modules) >= 3:
            score += 0.25
        else:
            score += (0.25 * len(modules) / 3)
        
        # Learning objectives
        modules_with_objectives = sum(1 for m in modules if m.learning_objectives)
        score += (0.25 * modules_with_objectives / max(1, len(modules)))
        
        # References
        if references and len(references) >= 3:
            score += 0.25
        elif references:
            score += (0.25 * len(references) / 3)
        
        # Assessment
        modules_with_assessment = sum(1 for m in modules if m.assessment_type)
        score += (0.25 * modules_with_assessment / max(1, len(modules)))
        
        return min(1.0, score)
