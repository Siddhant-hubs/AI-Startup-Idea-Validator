from crewai import Agent, Task, Crew, Process
import os
import json
from typing import Optional, List, Dict

def get_llm():
    # CrewAI expects a model string or a CrewAI BaseLLM here.
    # Use the same OpenRouter model format as crew_orchestrator.py.
    return os.getenv("CREWAI_MODEL", "openrouter/openai/gpt-4o-mini")

# In-memory knowledge base for current session
_knowledge_base: dict = {}

def ingest_knowledge(
    startup_idea: str,
    swot_data: Optional[dict] = None,
    mvp_data: Optional[dict] = None,
    gtm_data: Optional[dict] = None,
):
    """Ingest all validation outputs into the KB for the chatbot to use."""
    global _knowledge_base
    _knowledge_base = {
        "startup_idea": startup_idea,
        "swot_analysis": swot_data or {},
        "mvp_features": mvp_data or {},
        "gtm_strategy": gtm_data or {},
    }

def get_knowledge_base() -> dict:
    return _knowledge_base

def run_chatbot_query(user_question: str, startup_idea: str = "", conversation_history: Optional[List[Dict[str, str]]] = None) -> dict:
    llm = get_llm()

    kb = _knowledge_base
    kb_context = json.dumps(kb, indent=2) if kb else "No validation data available yet."

    history_str = ""
    if conversation_history:
        for msg in conversation_history[-6:]:  # last 3 exchanges
            history_str += f"{msg['role'].upper()}: {msg['content']}\n"

    advisor_agent = Agent(
        role="Startup Advisor & FAQ Expert",
        goal=(
            "Answer follow-up questions about the validated startup idea using the knowledge base "
            "from previous analysis. Provide actionable, specific advice based on SWOT, MVP, and GTM data. "
            "Be conversational, concise, and helpful."
        ),
        backstory=(
            "You are an experienced startup mentor who has guided 200+ founders. You have access to "
            "the full validation report for this startup and can answer detailed questions about strategy, "
            "risks, features, go-to-market approach, and more."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    chat_task = Task(
        description=f"""
        You are a conversational startup advisor. Answer the user's question using the knowledge base below.

        === KNOWLEDGE BASE ===
        {kb_context}

        === STARTUP IDEA ===
        {startup_idea if startup_idea else kb.get('startup_idea', 'Not specified')}

        === CONVERSATION HISTORY ===
        {history_str if history_str else 'This is the first message.'}

        === USER QUESTION ===
        {user_question}

        Generate your response ONLY as a valid JSON object:
        {{
            "answer": "Your detailed conversational answer here. Be specific, reference the knowledge base data when relevant.",
            "follow_up_suggestions": ["suggested question 1", "suggested question 2", "suggested question 3"],
            "confidence": "high/medium/low",
            "referenced_sections": ["SWOT", "MVP", "GTM", "General"]
        }}

        Rules:
        - Reference actual data from the knowledge base when possible
        - If KB is empty, answer from general startup knowledge
        - Be conversational but precise
        - Follow-up suggestions should be relevant next questions the user might want to ask
        - Return ONLY valid JSON, no markdown, no backticks
        """,
        agent=advisor_agent,
        expected_output="A valid JSON with the advisor's answer and follow-up suggestions",
    )

    crew = Crew(
        agents=[advisor_agent],
        tasks=[chat_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    raw = str(result).strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "answer": raw,
            "follow_up_suggestions": [],
            "confidence": "low",
            "referenced_sections": []
        }
