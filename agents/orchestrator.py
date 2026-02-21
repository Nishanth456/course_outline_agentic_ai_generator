"""PHASE 0: Orchestrator stub (will evolve through phases)."""

from agents.base import OrchestratorAgent


class CourseOrchestratorAgent(OrchestratorAgent):
    """
    Main orchestration implementation.
    
    Evolution:
    - PHASE 2: Single-pass, calls Module Creation Agent only
    - PHASE 3: Adds Retrieval Agent (parallel)
    - PHASE 4: Adds Web Search Agent (parallel)
    - PHASE 6: Adds Validator Agent loop + retries
    - PHASE 7: Integrates Query Agent for follow-ups
    """
    
    pass
