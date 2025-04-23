from typing import Dict, List
from find_applicable_talent.reasoning_interface.model_interfaces import ModelInterface
from typing import Callable, Any
from find_applicable_talent.util.logger import get_logger


logger = get_logger(__name__)


async def run_prompt_with_parser(
    prompt_builder: Callable[..., str],
    response_parser: Callable[[str], Any],
    model: ModelInterface,
    *args,
    **kwargs,
) -> Any:
    """
    Executes a full prompt lifecycle: builds prompt, runs LLM, and parses response.

    Args:
        prompt_builder: function that takes arbitrary inputs and returns a string prompt.
        response_parser: function that takes a string response and returns parsed output.
        llm_call: function that sends a prompt to the LLM and returns the raw response.
        *args, **kwargs: arguments to pass to the prompt_builder.

    Returns:
        Parsed result from response_parser
    """
    if model.api_key is None or getattr(model, "api_key", None) is None:
        logger.error("No API key found for model")
        raise ValueError("No API key found for model")
    else:
        logger.info(f"Request has API Key")
    prompt = prompt_builder(*args, **kwargs)
    logger.info(f"Prompt: {prompt}")
    response = await model.call_model(prompt)
    logger.info(f"Response: {response}")
    return response_parser(response)


def build_candidate_assignment_prompt(role_to_criteria: Dict[str, str], candidates: List[str]) -> str:
    return (
        "You are an AI recruiter. You have the following open roles and associated hiring criteria:\n"
        + "\n".join(f"- {role}: {criteria}" for role, criteria in role_to_criteria.items()) + "\n\n"
        "You also have the following candidates, pre-filtered and formatted as JSON objects:\n"
        + "\n".join(f"Candidate: {c}" for c in candidates) + "\n\n"
        "Assign candidates round-robin style to roles, prioritizing best match based on:\n"
        "- Skill alignment\n"
        "- School/job prestige\n"
        "- Recency of graduation (younger candidates may be more available)\n\n"
        "Output a list of role → candidate assignments with short explanations."
    )
