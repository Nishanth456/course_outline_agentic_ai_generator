"""
Main Streamlit app entry point (PHASE 1+).

PHASE 1:
- UI structure locked
- Input form (schema-bound)
- Session management
- PDF upload (ephemeral)
- Mock orchestrator
- Output rendering
- Error handling

Workflow:
1. User fills form → UserInputSchema
2. Upload PDF (optional) → temp storage
3. Click "Generate Outline" → Orchestrator
4. Display CourseOutlineSchema
"""

import streamlit as st
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

# Imports
from utils.session import SessionManager
from schemas.user_input import (
    UserInputSchema, AudienceLevel, AudienceCategory,
    LearningMode, DepthRequirement
)
from agents.orchestrator import CourseOrchestratorAgent
from tools.pdf_loader import PDFProcessor
import json


# ============================================================================
# INITIALIZATION & GLOBAL STATE
# ============================================================================

def init_session_manager():
    """Initialize session manager (stored in st.session_state)."""
    if "session_manager" not in st.session_state:
        st.session_state.session_manager = SessionManager(ttl_minutes=30)
    return st.session_state.session_manager


def init_session():
    """Initialize or recover current user session."""
    sm = init_session_manager()
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = sm.create_session()
    
    return st.session_state.session_id


def get_session_data() -> Optional[Dict[str, Any]]:
    """Get current session data."""
    sm = init_session_manager()
    session_id = st.session_state.get("session_id")
    return sm.get_session(session_id)


def update_session_data(key: str, value: Any):
    """Update current session."""
    sm = init_session_manager()
    session_id = st.session_state.get("session_id")
    if session_id:
        sm.update_session(session_id, key, value)


# ============================================================================
# UI SECTIONS
# ============================================================================

def render_header():
    """Render app header."""
    st.set_page_config(
        page_title="Course AI Agent",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    st.title("📚 Course Outline Generator")
    st.markdown(
        "Create comprehensive, educator-friendly course outlines. "
        "Combine your expertise with intelligent synthesis."
    )


def render_input_form() -> tuple[Optional[UserInputSchema], Optional[str]]:
    """
    Render input form in persistent left sidebar (STEP 1.2).
    
    Returns:
        Tuple of (UserInputSchema if valid, PDF path if uploaded), (None, None) otherwise
    """
    with st.form("course_form", clear_on_submit=False):
        # Required text fields
        course_title = st.text_input(
            "Course Title *",
            placeholder="e.g., 'Introduction to Machine Learning'",
            help="Short, descriptive title"
        )
        
        duration_hours = st.number_input(
            "Duration (hours) *",
            min_value=1, max_value=500,
            value=40,
            help="Total course duration in hours"
        )
        
        # Course description
        course_description = st.text_area(
            "Course Description *",
            placeholder="Describe the course goals, scope, and key topics...",
            height=80,
            help="Free-text description of what this course covers"
        )
        
        # Dropdowns
        audience_level = st.selectbox(
            "Audience Level *",
            options=[level.value for level in AudienceLevel],
            format_func=lambda x: x.replace("_", " ").title(),
            help="Educational level of your target learners"
        )
        
        audience_category = st.selectbox(
            "Audience Background *",
            options=[cat.value for cat in AudienceCategory],
            format_func=lambda x: x.replace("_", " ").title(),
            help="Professional or educational background"
        )
        
        learning_mode = st.selectbox(
            "Learning Mode *",
            options=[mode.value for mode in LearningMode],
            format_func=lambda x: x.replace("_", " ").title(),
            help="How will the course be delivered?"
        )
        
        depth_requirement = st.selectbox(
            "Depth Requirement *",
            options=[depth.value for depth in DepthRequirement],
            format_func=lambda x: x.replace("_", " ").title(),
            help="Theoretical vs practical balance"
        )
        
        # Optional custom constraints
        custom_constraints = st.text_area(
            "Custom Constraints (Optional)",
            placeholder="e.g., 'Focus on accessibility', 'Include hands-on labs'",
            height=60,
        )
        
        # PDF upload in sidebar
        st.markdown("#### 📄 Reference Material")
        uploaded_file = st.file_uploader(
            "Upload a PDF (optional)",
            type=["pdf"],
            help="Your course syllabus, notes, or reference materials"
        )
        
        pdf_path = None
        if uploaded_file:
            session_data = get_session_data()
            if session_data:
                try:
                    file_path, metadata = PDFProcessor.save_uploaded_pdf(
                        uploaded_file, session_data["temp_dir"]
                    )
                    pdf_path = file_path
                    st.success(f"✅ {metadata['filename']} uploaded")
                except Exception as e:
                    st.error(f"❌ Upload failed: {str(e)}")
        
        # Submit button
        submitted = st.form_submit_button("✨ Generate Outline", use_container_width=True)

    if submitted:
        # Validate required fields
        if not course_title or not course_description or not audience_level or not learning_mode:
            st.error("❌ Please fill all required fields marked with *")
            return None, None
        
        try:
            # Create schema
            user_input = UserInputSchema(
                course_title=course_title,
                course_description=course_description,
                audience_level=AudienceLevel(audience_level),
                audience_category=AudienceCategory(audience_category),
                learning_mode=LearningMode(learning_mode),
                depth_requirement=DepthRequirement(depth_requirement),
                duration_hours=int(duration_hours),
                custom_constraints=custom_constraints if custom_constraints else None,
                pdf_path=pdf_path,  # Set from inline upload
            )
            
            return user_input, pdf_path
        
        except Exception as e:
            st.error(f"❌ Validation error: {str(e)}")
            return None, None
    
    return None, None





def render_output_panel(outline_dict: Dict[str, Any]):
    """
    Render generated course outline (STEP 1.7).
    
    Args:
        outline_dict: CourseOutlineSchema dict
    """
    st.subheader("📖 Generated Course Outline")
    
    # Course summary card
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Duration", f"{outline_dict.get('total_duration_hours', 0)} hours")
    
    with col2:
        modules_count = len(outline_dict.get("modules", []))
        st.metric("Modules", modules_count)
    
    with col3:
        outcomes = outline_dict.get("course_level_learning_outcomes", [])
        st.metric("Learning Outcomes", len(outcomes))
    
    # Course summary
    st.markdown("### 📋 Course Summary")
    st.write(outline_dict.get("course_summary", ""))
    
    # Audience info
    st.markdown("### 👥 Target Audience")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.caption("Level")
        st.write(outline_dict.get("audience_level", "").replace("_", " ").title())
    with col2:
        st.caption("Category")
        st.write(outline_dict.get("audience_category", "").replace("_", " ").title())
    with col3:
        st.caption("Mode")
        st.write(outline_dict.get("learning_mode", "").replace("_", " ").title())
    with col4:
        st.caption("Depth")
        st.write(outline_dict.get("depth_requirement", "").replace("_", " ").title())
    
    # Prerequisites
    if outline_dict.get("prerequisites"):
        st.markdown("### 📚 Prerequisites")
        for prereq in outline_dict["prerequisites"]:
            st.write(f"- {prereq}")
    
    # Course-level learning outcomes
    if outline_dict.get("course_level_learning_outcomes"):
        st.markdown("### 🎯 Course-Level Learning Outcomes")
        for lo in outline_dict["course_level_learning_outcomes"]:
            with st.container():
                st.write(f"**{lo['objective_id']}:** {lo['statement']}")
                st.caption(f"Bloom's Level: {lo['bloom_level'].title()}")
    
    # Modules (expandable)
    st.markdown("### 📚 Course Modules")
    
    modules = outline_dict.get("modules", [])
    for module in modules:
        with st.expander(f"**{module['title']}** ({module['estimated_hours']:.1f} hours)"):
            st.write(module["synopsis"])
            
            # Module learning objectives
            st.markdown("#### Learning Objectives")
            for lo in module.get("learning_objectives", []):
                st.write(f"- {lo['statement']} ({lo['bloom_level'].title()})")
            
            # Module lessons
            st.markdown("#### Lessons")
            for lesson in module.get("lessons", []):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📌 {lesson['title']}")
                with col2:
                    st.caption(f"{lesson['duration_minutes']} min")
            
            # Assessment
            if module.get("assessment"):
                st.markdown("#### Assessment")
                assessment = module["assessment"]
                st.write(f"**Type:** {assessment.get('type', 'N/A').title()}")
                st.write(f"**Weight:** {assessment.get('weight', 0):.1%}")
    
    # Capstone project
    capstone = outline_dict.get("capstone_project")
    if capstone:
        st.markdown("### 🏆 Capstone Project")
        st.write(f"**{capstone['title']}**")
        st.write(f"*Scope:* {capstone['scope']}")
        if capstone.get("deliverables"):
            st.markdown("**Deliverables:**")
            for deliverable in capstone["deliverables"]:
                st.write(f"- {deliverable}")
    
    # Recommended tools
    if outline_dict.get("recommended_tools"):
        st.markdown("### 🛠️ Recommended Tools & Technologies")
        tools = outline_dict["recommended_tools"]
        st.write(", ".join(tools) if tools else "None")
    
    # Instructor notes
    if outline_dict.get("instructor_notes"):
        st.markdown("### 📌 Instructor Notes")
        st.info(outline_dict["instructor_notes"])
    
    # Dev/debug section
    if st.session_state.get("debug_mode", False):
        st.markdown("---")
        st.markdown("### 🔧 Debug Info")
        if st.checkbox("Show raw JSON"):
            st.json(outline_dict)
        
        st.caption("Schema validation: ✅ Valid")


def render_sidebar_controls():
    """Render sidebar controls (reset, debug) in persistent left column."""
    st.markdown("---")
    st.markdown("### ⚙️ Controls")
    
    # Reset button
    if st.button("🔄 Reset Session", use_container_width=True):
        sm = init_session_manager()
        session_id = st.session_state.get("session_id")
        if session_id:
            sm.cleanup_session(session_id)
        
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        st.success("✅ Session reset. Refresh to continue.")
        st.stop()
    
    # Debug toggle
    st.markdown("---")
    debug_mode = st.checkbox("Debug Mode", value=False)
    update_session_data("debug_mode", debug_mode)
    
    # Session info (debug)
    if debug_mode:
        st.markdown("### Session Info")
        session_data = get_session_data()
        if session_data:
            st.caption(f"Session ID: {session_data['session_id'][:8]}...")
            st.caption(f"Created: {session_data['created_at'].strftime('%H:%M:%S')}")
            if session_data.get("current_outline"):
                st.caption("✅ Outline generated")


# ============================================================================
# MAIN APP FLOW
# ============================================================================

def main():
    """Main Streamlit app (STEPS 1.1-1.8) with persistent left sidebar."""
    
    # Initialize
    render_header()
    init_session()
    
    # Create persistent two-column layout: 25% left sidebar, 75% right content
    col_left, col_right = st.columns([1, 3], gap="medium")
    
    # LEFT COLUMN: Input form and controls (persistent sidebar)
    with col_left:
        st.markdown("### 📝 Course Details")
        user_input, pdf_path = render_input_form()
        render_sidebar_controls()
    
    # RIGHT COLUMN: Main content area (scrollable)
    with col_right:
        if user_input:
            # Store PDF path in session if uploaded
            if pdf_path:
                update_session_data("uploaded_pdf_path", pdf_path)
            
            # Generate outline
            st.info("⏳ Generating course outline...")
            
            try:
                # Call orchestrator
                orchestrator = CourseOrchestratorAgent()
                
                # Run async agent
                outline = asyncio.run(orchestrator.run(user_input.model_dump()))
                
                # Store in session
                update_session_data("current_outline", outline)
                update_session_data("user_input", user_input.model_dump())
                update_session_data("run_id", outline.get("generated_by_agent", ""))
                
                # Render output
                st.success("✅ Course outline generated!")
                st.balloons()
                render_output_panel(outline)
            
            except Exception as e:
                st.error(f"❌ Generation failed: {str(e)}")
                
                if st.session_state.get("debug_mode", False):
                    st.exception(e)
        else:
            # Show existing outline from session
            session_data = get_session_data()
            if session_data and session_data.get("current_outline"):
                render_output_panel(session_data["current_outline"])
            else:
                st.markdown(
                    "<div style='text-align: center; padding: 80px 20px;'>"
                    "<h2>👈 Course Details</h2>"
                    "<p>Fill in the course details in the left sidebar to generate an outline</p>"
                    "</div>",
                    unsafe_allow_html=True
                )


if __name__ == "__main__":
    main()
