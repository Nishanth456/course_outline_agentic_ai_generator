"""
PHASE 0: Contract for user input.

Validates frontend form submissions.
This is the first contract any agent receives.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class AudienceLevel(str, Enum):
    """Audience / educational level."""
    HIGH_SCHOOL = "high_school"
    UNDERGRADUATE = "undergraduate"
    POSTGRADUATE = "postgraduate"
    PROFESSIONAL = "professional"


class AudienceCategory(str, Enum):
    """Audience background / role."""
    CS_MAJOR = "cs_major"
    NON_CS_DOMAIN = "non_cs_domain"
    INDUSTRY_PROFESSIONAL = "industry_professional"
    SELF_LEARNER = "self_learner"


class LearningMode(str, Enum):
    """How content is delivered."""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    HYBRID = "hybrid"


class DepthRequirement(str, Enum):
    """How deep / theoretical vs practical."""
    CONCEPTUAL = "conceptual"
    APPLIED = "applied"
    IMPLEMENTATION = "implementation"
    RESEARCH = "research"


class UserInputSchema(BaseModel):
    """
    Educator input from Streamlit UI (PHASE 1).
    
    This is the entry point for the orchestrator.
    All fields are required except pdf_path (optional upload).
    """
    
    course_title: str = Field(
        ..., 
        description="e.g., 'Introduction to Machine Learning'"
    )
    
    course_description: str = Field(
        ..., 
        description="Free-text description of course goals and scope"
    )
    
    audience_level: AudienceLevel = Field(
        ..., 
        description="Target educational level"
    )
    
    audience_category: AudienceCategory = Field(
        ..., 
        description="Learner background / role"
    )
    
    learning_mode: LearningMode = Field(
        ..., 
        description="Delivery method"
    )
    
    depth_requirement: DepthRequirement = Field(
        ..., 
        description="Depth / theory vs practice balance"
    )
    
    duration_hours: int = Field(
        ..., 
        ge=1, 
        le=500, 
        description="Total course duration in hours"
    )
    
    pdf_path: Optional[str] = Field(
        None, 
        description="Path to uploaded session PDF (temp storage, PHASE 1)"
    )
    
    custom_constraints: Optional[str] = Field(
        None, 
        description="Free-text additional requirements/constraints"
    )
    
    class Config:
        """Pydantic config."""
        use_enum_values = True
