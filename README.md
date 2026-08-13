AUTONOMOUS AI AGENTS WITH RECURSIVE WEB RETRIEVAL AND AUTOMATED SYNTHESIS

Canonical implementation:
- `multi_agents/` is the active research workflow and contains the single source of truth for the agent orchestration.
- `backend/` provides the API and web integration layers against that workflow.
- `gpt_researcher/` contains the core retrieval and synthesis engine.
- Duplicate experimental agent variants were removed to keep one implementation path with the combined feature set.