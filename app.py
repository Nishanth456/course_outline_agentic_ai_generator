"""Main Streamlit app entry point (PHASE 1+)."""

import streamlit as st
from typing import Optional, Dict, Any

# PHASE 0: This is a skeleton.
# PHASE 1: Add UI components
# PHASE 2+: Integrate orchestrator


def main():
    """
    Streamlit main app.
    
    Workflow:
    1. User fills form (PHASE 1)
    2. Click "Generate Outline" (PHASE 2)
    3. Display results + edit UI (PHASE 8)
    4. Download or ask follow-ups (PHASE 7)
    """
    
    st.set_page_config(
        page_title="Course AI Agent",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 Course Outline Generator AI")
    st.markdown(
        "Create comprehensive course outlines powered by AI. "
        "Combine your expertise with intelligent synthesis."
    )
    
    # TODO: PHASE 1 - Add UI form
    # TODO: PHASE 2 - Integrate orchestrator
    # TODO: PHASE 8 - Add editing and export
    
    st.info("🚀 Project initialized. Phases will be implemented incrementally.")


if __name__ == "__main__":
    main()
