from crewai import Agent, Task, Crew, Process
import os
import json

def get_llm():
    # CrewAI expects a model string or a CrewAI BaseLLM here.
    # Use the same OpenRouter model format as crew_orchestrator.py.
    return os.getenv("CREWAI_MODEL", "openrouter/openai/gpt-4o-mini")

def run_swot_risk_analysis(startup_idea: str, market_context: str = "") -> dict:
    llm = get_llm()

    swot_agent = Agent(
        role="SWOT & Risk Analyst",
        goal=(
            "Perform a detailed SWOT analysis and risk assessment for the given startup idea. "
            "Identify internal strengths and weaknesses, external opportunities and threats, "
            "and predict key business risks using LLM reasoning."
        ),
        backstory=(
            "You are a senior startup strategist with 15+ years of experience in venture capital "
            "and business analysis. You specialize in evaluating early-stage startups with deep "
            "frameworks like SWOT, PESTLE, and Monte Carlo risk modeling."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    swot_task = Task(
        description=f"""
        Analyze the following startup idea and perform a comprehensive SWOT & Risk Analysis.

        Startup Idea: {startup_idea}
        Market Context (if available): {market_context if market_context else 'Not provided'}

        Generate your response ONLY as a valid JSON object with this exact structure:
        {{
            "swot": {{
                "strengths": ["strength 1", "strength 2", "strength 3", "strength 4"],
                "weaknesses": ["weakness 1", "weakness 2", "weakness 3", "weakness 4"],
                "opportunities": ["opportunity 1", "opportunity 2", "opportunity 3", "opportunity 4"],
                "threats": ["threat 1", "threat 2", "threat 3", "threat 4"]
            }},
            "risk_analysis": {{
                "high_risks": [
                    {{"risk": "risk name", "description": "detailed description", "mitigation": "how to mitigate"}}
                ],
                "medium_risks": [
                    {{"risk": "risk name", "description": "detailed description", "mitigation": "how to mitigate"}}
                ],
                "low_risks": [
                    {{"risk": "risk name", "description": "detailed description", "mitigation": "how to mitigate"}}
                ]
            }},
            "competitor_risk": {{
                "top_competitors": ["competitor 1", "competitor 2", "competitor 3"],
                "market_saturation": "low/medium/high",
                "differentiation_score": "X/10",
                "competitive_advantage": "brief description"
            }},
            "market_demand_prediction": {{
                "demand_level": "low/medium/high/very high",
                "growth_trajectory": "declining/stable/growing/explosive",
                "target_market_size": "estimated size",
                "prediction_reasoning": "2-3 sentence reasoning"
            }},
            "overall_risk_score": "X/10 (10 = highest risk)",
            "summary": "2-3 sentence executive summary of risks and strengths"
        }}

        Return ONLY the JSON. No markdown, no explanation, no backticks.
        """,
        agent=swot_agent,
        expected_output="A valid JSON object with SWOT analysis and risk assessment",
    )

    crew = Crew(
        agents=[swot_agent],
        tasks=[swot_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    raw = str(result).strip()

    # Clean up if model returns markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"error": "Failed to parse SWOT analysis", "raw": raw}
