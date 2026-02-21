"""
PHASE 2: Module Creation Agent

Core curriculum synthesis engine.

Responsibilities:
- Accept ExecutionContext (structured input)
- Call LLMService with prompt template
- Parse LLM response into CourseOutlineSchema
- Handle token limits and retries
- Return validated outline

NOT responsible for:
- Orchestration logic (Orchestrator's job)
- Input validation (UserInputSchema validates before this agent)
- Web search (Phase 4)
- PDF retrieval (Phase 3)
- Retry coordination (Phase 6)

⚠️ Phase 2 Constraint: Agent receives ExecutionContext.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from schemas.user_input import UserInputSchema
from schemas.course_outline import (
    CourseOutlineSchema, Module, Lesson, LearningObjective, BloomLevel
)
from schemas.execution_context import ExecutionContext
import random
import math

logger = logging.getLogger(__name__)


class CoreModuleCreationAgent:
    """
    Module creation engine for Phase 2.
    
    MOCK IMPLEMENTATION: Generates template-driven outlines.
    REAL IMPLEMENTATION: Calls LLMService for synthesis.
    
    API:
    - Input: ExecutionContext
    - Output: CourseOutlineSchema
    """
    
    async def run(self, context: ExecutionContext) -> CourseOutlineSchema:
        """
        Generate course outline from execution context.

        Args:
            context: ExecutionContext containing user_input and metadata
            
        Returns:
            CourseOutlineSchema with generated outline
            
        Raises:
            ValueError: If context invalid or output doesn't match schema
        """
        
        # Phase 2: MOCK IMPLEMENTATION (template-driven)
        # Real Phase 5: This would call LLMService
        
        # Extract user input
        user_input = context.user_input
        if not user_input:
            raise ValueError("user_input required in ExecutionContext")
        
        logger.debug(
            "Generating course outline",
            extra={"execution_id": context.execution_id}
        )
        
        # Generate mock outline
        outline = self._generate_mock_outline(user_input)
        
        # Validate schema
        if not isinstance(outline, CourseOutlineSchema):
            raise ValueError(f"Expected CourseOutlineSchema, got {type(outline)}")
        
        logger.debug(
            "Course outline generated",
            extra={
                "execution_id": context.execution_id,
                "modules": len(outline.modules),
            }
        )
        
        return outline
    
    def _generate_mock_outline(self, user_input: UserInputSchema) -> CourseOutlineSchema:
        """
        Generate mock course outline respecting user constraints.
        
        PHASE 2: Template-driven, no AI.
        Returns CourseOutlineSchema (not dict).
        """
        # Validate input type
        if isinstance(user_input, dict):
            user_input = UserInputSchema(**user_input)
        elif not isinstance(user_input, UserInputSchema):
            raise ValueError(f"Expected UserInputSchema, got {type(user_input)}")
        
        # Calculate module count based on duration
        total_hours = user_input.duration_hours
        num_modules = max(2, min(6, math.ceil(total_hours / 5)))  # 5 hours per module avg
        
        # Calculate hours per module
        hours_per_module = total_hours / num_modules
        
        # Generate modules
        modules = []
        for i in range(num_modules):
            module = self._generate_mock_module(
                module_num=i + 1,
                hours=hours_per_module,
                depth=user_input.depth_requirement,
                audience_level=user_input.audience_level,
                learning_mode=user_input.learning_mode,
            )
            modules.append(module)
        
        # Generate course-level learning outcomes
        course_level_outcomes = self._generate_course_outcomes(
            user_input, num_modules
        )
        
        # Build outline as CourseOutlineSchema
        outline = CourseOutlineSchema(
            course_title=user_input.course_title,
            course_summary=user_input.course_description[:200] + "...",
            audience_level=user_input.audience_level,
            audience_category=user_input.audience_category,
            learning_mode=user_input.learning_mode,
            depth_requirement=user_input.depth_requirement,
            total_duration_hours=total_hours,
            prerequisites=self._get_prerequisites(user_input),
            course_level_learning_outcomes=course_level_outcomes,
            modules=modules,
            capstone_project=self._generate_capstone(user_input),
            evaluation_strategy=self._generate_evaluation_strategy(),
            recommended_tools=self._get_recommended_tools(user_input),
            instructor_notes="This is a mock outline generated in Phase 2. "
                           "Full content synthesis coming in Phase 5.",
            citations_and_provenance=[],
            generated_by_agent="module_creation_agent",
            generation_timestamp=datetime.now().isoformat(),
        )
        
        return outline
    
    def _generate_mock_module(
        self,
        module_num: int,
        hours: float,
        depth: str,
        audience_level: str,
        learning_mode: str,
    ) -> Module:
        """Generate a single mock module."""
        
        # Topic templates
        topics = [
            "Foundations & Core Concepts",
            "Practical Application",
            "Advanced Techniques",
            "Real-World Case Studies",
            "Integration & Best Practices",
            "Capstone Preparation",
        ]
        
        topic = topics[module_num - 1] if module_num <= len(topics) else f"Module {module_num}"
        
        # Generate learning objectives (respect Bloom's level based on depth)
        num_objectives = random.randint(3, 5)
        learning_objectives = []
        
        bloom_levels = [
            BloomLevel.REMEMBER, BloomLevel.UNDERSTAND, BloomLevel.APPLY,
            BloomLevel.ANALYZE, BloomLevel.EVALUATE, BloomLevel.CREATE,
        ]
        
        for j in range(num_objectives):
            bloom = bloom_levels[min(j, len(bloom_levels) - 1)]
            if depth == "conceptual":
                bloom = BloomLevel.UNDERSTAND
            elif depth == "applied":
                bloom = BloomLevel.APPLY
            elif depth == "implementation":
                bloom = BloomLevel.CREATE
            
            objectives = {
                "remember": f"Recall {topic.lower()} definitions and terminology",
                "understand": f"Explain the principles of {topic.lower()}",
                "apply": f"Apply {topic.lower()} techniques to solve problems",
                "analyze": f"Analyze {topic.lower()} structures and patterns",
                "evaluate": f"Evaluate {topic.lower()} approaches and trade-offs",
                "create": f"Create a custom {topic.lower()} implementation",
            }
            
            lo = LearningObjective(
                objective_id=f"LO_{module_num}_{j + 1}",
                statement=objectives.get(bloom.value, f"Master {topic.lower()}"),
                bloom_level=bloom,
                assessment_method="Quiz" if bloom in [BloomLevel.REMEMBER, BloomLevel.UNDERSTAND] else "Hands-on"
            )
            learning_objectives.append(lo)
        
        # Generate lessons
        num_lessons = random.randint(2, 4)
        lesson_duration = int((hours * 60) / num_lessons)
        
        lessons = []
        for k in range(num_lessons):
            lesson = Lesson(
                lesson_id=f"L_{module_num}_{k + 1}",
                title=f"{topic} - Part {k + 1}",
                duration_minutes=max(15, lesson_duration),
                activities=self._get_activities(learning_mode),
                assessment_type="Quiz" if k == num_lessons - 1 else None,
                resources=[]
            )
            lessons.append(lesson)
        
        # Create module
        module = Module(
            module_id=f"M_{module_num}",
            title=f"Module {module_num}: {topic}",
            synopsis=f"This module covers {topic.lower()} and related concepts.",
            estimated_hours=hours,
            learning_objectives=learning_objectives,
            lessons=lessons,
            assessment={
                "type": "quiz",
                "weight": 0.1 * (module_num / 6),
                "rubric": "Mastery of key concepts"
            },
            bloom_level=learning_objectives[-1].bloom_level,
            keywords=[word.lower() for word in topic.split()],
            readings_and_resources=[],
        )
        
        return module
    
    def _generate_course_outcomes(
        self, user_input: UserInputSchema, num_modules: int
    ) -> List[LearningObjective]:
        """Generate course-level learning outcomes."""
        
        outcomes = [
            LearningObjective(
                objective_id="CO_1",
                statement=f"Understand the core concepts of {user_input.course_title}",
                bloom_level=BloomLevel.UNDERSTAND,
                assessment_method="Quizzes and assignments"
            ),
            LearningObjective(
                objective_id="CO_2",
                statement=f"Apply knowledge from {user_input.course_title} to real-world scenarios",
                bloom_level=BloomLevel.APPLY,
                assessment_method="Projects and case studies"
            ),
            LearningObjective(
                objective_id="CO_3",
                statement=f"Critically evaluate topics in {user_input.course_title}",
                bloom_level=BloomLevel.EVALUATE,
                assessment_method="Final exam or capstone"
            ),
        ]
        
        return outcomes
    
    def _generate_capstone(self, user_input: UserInputSchema) -> Dict[str, Any]:
        """Generate capstone project."""
        return {
            "title": f"{user_input.course_title} Capstone Project",
            "scope": "Comprehensive project combining all course modules",
            "deliverables": ["Project proposal", "Implementation", "Documentation", "Presentation"],
            "rubric": {"completeness": 25, "correctness": 25, "documentation": 25, "presentation": 25}
        }
    
    def _generate_evaluation_strategy(self) -> Dict[str, Any]:
        """Generate evaluation strategy."""
        return {
            "formative": ["Quizzes", "Homework", "Peer review"],
            "summative": ["Final exam", "Capstone project"],
            "rubrics": {"accuracy": 40, "completeness": 30, "clarity": 30}
        }
    
    def _get_prerequisites(self, user_input: UserInputSchema) -> List[str]:
        """Get prerequisites based on audience and depth."""
        if user_input.audience_level == "high_school":
            return ["Basic math", "Computer literacy"]
        elif user_input.audience_level == "undergraduate":
            return ["Intro-level knowledge in related field"]
        elif user_input.audience_level == "postgraduate":
            return ["Bachelor's degree in related field"]
        else:  # professional
            return ["2+ years professional experience"]
    
    def _get_activities(self, learning_mode: str) -> List[str]:
        """Get recommended activities based on learning mode."""
        if learning_mode == "synchronous":
            return ["Live lecture", "Q&A session", "Group discussion"]
        elif learning_mode == "asynchronous":
            return ["Video watching", "Asynchronous discussion forum", "Self-paced practice"]
        else:  # hybrid
            return ["Live session", "Recorded content", "Self-paced exercises", "Group project"]
    
    def _get_recommended_tools(self, user_input: UserInputSchema) -> List[str]:
        """Get recommended tools based on course."""
        tools = []
        if "data" in user_input.course_title.lower():
            tools = ["Python", "Jupyter Notebook", "Pandas", "PostgreSQL"]
        elif "machine learning" in user_input.course_title.lower():
            tools = ["Python", "TensorFlow/PyTorch", "Scikit-learn", "Jupyter Notebook"]
        elif "web" in user_input.course_title.lower():
            tools = ["VS Code", "Node.js", "React", "Chrome DevTools"]
        else:
            tools = ["IDE", "Version Control", "Documentation Tools"]
        
        return tools
