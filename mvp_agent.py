from crewai import Agent, Task, Crew, Process
import os
import json

def get_llm():
    # CrewAI expects a model string or a CrewAI BaseLLM here.
    # Use the same OpenRouter model format as crew_orchestrator.py.
    return os.getenv("CREWAI_MODEL", "openrouter/openai/gpt-4o-mini")

def run_mvp_analysis(startup_idea: str, swot_context: str = "") -> dict:
    llm = get_llm()

    mvp_agent = Agent(
        role="MVP Product Strategist",
        goal=(
            "Prioritize and recommend the core MVP features for the given startup idea "
            "using the MoSCoW framework (Must Have, Should Have, Could Have, Won't Have). "
            "Focus on market fit and resource constraints for an early-stage startup."
        ),
        backstory=(
            "You are a seasoned product manager who has helped 50+ startups launch their MVPs. "
            "You use lean startup methodology, MoSCoW prioritization, and Jobs-To-Be-Done framework "
            "to identify the minimum set of features that deliver maximum value."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    mvp_task = Task(
        description=f"""
        For the following startup idea, define a comprehensive MVP feature set using the MoSCoW framework.

        Startup Idea: {startup_idea}
        SWOT Context (if available): {swot_context if swot_context else 'Not provided'}

        Generate your response ONLY as a valid JSON object with this exact structure:
        {{
            "moscow_framework": {{
                "must_have": [
                    {{
                        "feature": "feature name",
                        "reason": "why this is critical",
                        "effort": "low/medium/high",
                        "impact": "low/medium/high"
                    }}
                ],
                "should_have": [
                    {{
                        "feature": "feature name",
                        "reason": "why this adds value",
                        "effort": "low/medium/high",
                        "impact": "low/medium/high"
                    }}
                ],
                "could_have": [
                    {{
                        "feature": "feature name",
                        "reason": "nice to have",
                        "effort": "low/medium/high",
                        "impact": "low/medium/high"
                    }}
                ],
                "wont_have": [
                    {{
                        "feature": "feature name",
                        "reason": "why excluded from MVP"
                    }}
                ]
            }},
            "tech_stack_recommendation": {{
                "frontend": "recommended tech",
                "backend": "recommended tech",
                "database": "recommended tech",
                "ai_ml": "recommended tech if applicable",
                "deployment": "recommended platform",
                "reasoning": "brief reasoning"
            }},
            "mvp_timeline": {{
                "phase_1": {{"duration": "X weeks", "focus": "description"}},
                "phase_2": {{"duration": "X weeks", "focus": "description"}},
                "phase_3": {{"duration": "X weeks", "focus": "description"}}
            }},
            "resource_requirements": {{
                "team_size": "X-Y people",
                "budget_estimate": "$X - $Y",
                "key_roles": ["role 1", "role 2", "role 3"]
            }},
            "success_metrics": ["metric 1", "metric 2", "metric 3", "metric 4"],
            "mvp_summary": "2-3 sentence summary of the MVP strategy"
        }}

        Must Have should have 4-5 features, Should Have 3-4, Could Have 3-4, Won't Have 2-3.
        Return ONLY the JSON. No markdown, no explanation, no backticks.
        """,
        agent=mvp_agent,
        expected_output="A valid JSON object with MoSCoW feature prioritization",
    )

    crew = Crew(
        agents=[mvp_agent],
        tasks=[mvp_task],
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
        return {"error": "Failed to parse MVP analysis", "raw": raw}
