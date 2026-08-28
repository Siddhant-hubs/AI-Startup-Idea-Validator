from crewai import Agent, Task, Crew, Process
import os
import json

def get_llm():
    # CrewAI expects a model string or a CrewAI BaseLLM here.
    # Use the same OpenRouter model format as crew_orchestrator.py.
    return os.getenv("CREWAI_MODEL", "openrouter/openai/gpt-4o-mini")

def run_gtm_analysis(startup_idea: str, swot_context: str = "", mvp_context: str = "") -> dict:
    llm = get_llm()

    gtm_agent = Agent(
        role="Go-To-Market Strategist",
        goal=(
            "Develop a comprehensive Go-To-Market strategy for the startup idea, including "
            "positioning, distribution channels, pricing strategy, and early customer acquisition approach. "
            "Answer the core question: 'How do we get our first 1000 customers?'"
        ),
        backstory=(
            "You are a growth marketing expert who has launched products at top-tier startups. "
            "You specialize in early-stage GTM strategies, product-led growth, community building, "
            "and performance marketing with lean budgets."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    gtm_task = Task(
        description=f"""
        Develop a complete Go-To-Market strategy for the following startup idea.

        Startup Idea: {startup_idea}
        SWOT Context: {swot_context if swot_context else 'Not provided'}
        MVP Context: {mvp_context if mvp_context else 'Not provided'}

        Generate your response ONLY as a valid JSON object with this exact structure:
        {{
            "positioning": {{
                "value_proposition": "one clear sentence",
                "target_segment": "primary target customer",
                "unique_differentiator": "what makes this different",
                "positioning_statement": "For [target], [product] is the [category] that [benefit] because [reason]"
            }},
            "channels": {{
                "primary": [
                    {{
                        "channel": "channel name",
                        "strategy": "how to use it",
                        "expected_reach": "estimate",
                        "cost": "free/low/medium/high"
                    }}
                ],
                "secondary": [
                    {{
                        "channel": "channel name",
                        "strategy": "how to use it",
                        "cost": "free/low/medium/high"
                    }}
                ]
            }},
            "customer_acquisition": {{
                "first_100_customers": "specific strategy to get first 100 customers",
                "first_1000_customers": "strategy to scale to 1000 customers",
                "customer_acquisition_cost": "estimated CAC",
                "lifetime_value_estimate": "estimated LTV",
                "acquisition_tactics": ["tactic 1", "tactic 2", "tactic 3", "tactic 4", "tactic 5"]
            }},
            "pricing_strategy": {{
                "model": "freemium/subscription/one-time/usage-based/etc",
                "tiers": [
                    {{"name": "tier name", "price": "$X/month", "features": ["feature 1", "feature 2"]}}
                ],
                "reasoning": "why this pricing model"
            }},
            "launch_plan": {{
                "pre_launch": {{"duration": "X weeks", "activities": ["activity 1", "activity 2"]}},
                "launch_week": {{"activities": ["activity 1", "activity 2", "activity 3"]}},
                "post_launch": {{"duration": "X weeks", "activities": ["activity 1", "activity 2"]}}
            }},
            "key_partnerships": ["partner type 1", "partner type 2", "partner type 3"],
            "growth_metrics": {{
                "month_1_target": "X users/revenue",
                "month_3_target": "X users/revenue",
                "month_6_target": "X users/revenue"
            }},
            "gtm_summary": "2-3 sentence executive summary of the GTM strategy"
        }}

        Return ONLY the JSON. No markdown, no explanation, no backticks.
        """,
        agent=gtm_agent,
        expected_output="A valid JSON with complete Go-To-Market strategy",
    )

    crew = Crew(
        agents=[gtm_agent],
        tasks=[gtm_task],
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
        return {"error": "Failed to parse GTM analysis", "raw": raw}
