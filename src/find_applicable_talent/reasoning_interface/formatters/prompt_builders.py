from typing import List, Dict, Any
import json
from find_applicable_talent.core.candidate import Candidate


def build_role_ideation_prompt(startup_description: str) -> str:
    return (
        "You are the founder of a newly funded, fast-moving startup in software unless otherwise specified. You are currently the only employee.\n"
        f"Startup description: {startup_description}\n\n"
        "You need to hire 5 people to build out your core team. These hires should be:\n"
        "- High-agency, multi-talented individuals who can wear multiple hats\n"
        "- Focused on building and shipping product quickly\n"
        "- Diverse in role focus, spanning backend, frontend, machine learning, product, design, growth, or whatever is most relevant to the startup\n\n"
        "Make sure at least one role is focused on customer acquisition, growth, or user traction — this is essential at this stage.\n"
        "Do NOT include support roles like legal, finance, or HR.\n"
        "Instead, prioritize hires who can collectively own all key functions of a tech startup: product development, infrastructure, user growth, and execution.\n\n"
        "Return a bulleted list of 5 critical roles with a two-sentence justification each. Roles should be distinct but complementary.\n"
        "Do not include any other text or commentary. \n Response:"
    )


def build_role_refinement_prompt(current_roles: List[Dict[str, str]], user_feedback: str) -> str:
    return (
        "You are helping a solo founder of a newly funded software startup finalize the first 5 hires.\n\n"
        "Here is the current list of proposed roles:\n"
        + "\n".join(f"- {role['title']}: {role['justification']}" for role in current_roles) + "\n\n"
        f"The founder has provided this feedback:\n\"{user_feedback}\"\n\n"
        "Based on this feedback, revise the list. You may:\n"
        "- Reword, replace, or re-prioritize roles\n"
        "- Remove unnecessary roles and add better-fitting ones\n"
        "- Ensure the roles are distinct, cover core startup functions (e.g., product, backend, growth, etc.), and reflect the founder's intent\n\n"
        "Do not refer to previous messages or history — make this a complete, standalone list.\n"
        "Return a bulleted list of exactly 5 updated roles, each with a two-sentence rationale.\n"
        "Do not include any other text or commentary. \n Response:"
    )


def build_candidate_criteria_prompt(role: str) -> str:
    return (
        f"You are defining hiring criteria for a '{role}' role at a newly funded startup.\n\n"
        "Build a detailed and structured hiring rubric that accounts for different types of strong candidates.\n"
        "You should not assume there is only one 'ideal' candidate. Instead, define multiple viable archetypes that may be valuable for the role, such as:\n"
        "- A high-achieving early-career candidate with rapid growth potential and great academic pedigree\n"
        "- A mid-level candidate with proven execution in high-pressure environments (e.g., fast-paced startups)\n"
        "- A senior candidate with deep experience at elite companies known for high-quality engineering/product/growth cultures\n\n"
        "For each archetype, outline:\n"
        "- Which signals or traits matter most (e.g., graduation recency, school prestige, startup experience, company reputation, title trajectory)\n"
        "- Whether the role is technical or non-technical, and which skills are necessary vs. nice-to-have\n"
        "- What trade-offs you're willing to accept (e.g., less pedigree but more project ownership)\n"
        "- The specific values or behaviors you're selecting for (e.g., intensity, grit, creativity, independence)\n\n"
        "You may describe multiple 'tracks' or decision trees of candidate evaluation based on different strengths.\n"
        "Assign a weight (0-5) to each criterion to indicate its relative importance within each archetype.\n\n"
        "Do not include any other text or commentary. \n Response:"
    )


def build_candidate_round_robin_prompt(role: str, rubric:str, candidates: List[Candidate]) -> str:
    return (
        "You are an expert evaluator helping a startup assign candidates to roles using a detailed hiring rubric.\n\n"
        "You must remove legal, finance, and HR roles unless specifically called for by the job description.\n\n"
        "Each role below comes with a custom, in-depth rubric outlining what a strong candidate would look like. "
        "However, the candidate data is sparse — you'll need to make educated assumptions to fill in gaps.\n\n"
        "Use features such as:\n"
        "- Graduation year (`most_recent_end_date`) to infer age and availability\n"
        "- Start year of undergraduate to approximate age and experience window\n"
        "- Patterns in job titles and company names to guess career trajectory, seniority, or culture fit\n"
        "- School prestige flags (e.g. Top 25 / Top 50) for educational signal\n"
        "- Location, role history, or side gigs (e.g., freelance work) to guess hustle, adaptability, or grit\n\n"
        "There are multiple open roles, and your task is to assign **exactly one candidate to each role** in a round-robin fashion — "
        "choose the best match for each role based on inference and alignment with the rubric.\n\n"
        "Remember that the slope is more important than the y-intercept. Youthful work ethic is important and needs high credentials to offset.\n"
        "Also Remember that my startup is in the United States so we should bias towards candidates who have worked in the United States, but do not exclude candidates with great pedigree.\n\n"
        f"The roles and their rubrics are as follows:\n\n" +
        f"Role: {role}\nRubric:\n{rubric} \n\n" +
        "Here are the available candidates:\n" +
        "\n".join(
            f"Candidate ID: {c.id}\n" + json.dumps(c.to_llm_dict(), indent=2)
            for c in candidates
        ) + "\n\n"        
        "Assign the best candidate to each role. Be opinionated, make bold assumptions, and justify them only to yourself — "
        "the output should contain only the `user_id` of the candidate best suited for the role.\n\n"
        "Respond strictly in the following JSON format — do not include any additional text or markdown:\n"
        "{\n"
        '  "selected_user_id": "<ID of selected candidate>",\n'
        '  "explanation": "<A short, maximum 5-sentence explanation of why this candidate is the best fit>"\n'
        "}\n\n"
        "Response:"
    )

