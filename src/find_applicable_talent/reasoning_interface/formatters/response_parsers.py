import re
import json
from typing import List, Dict, Any
from find_applicable_talent.util.logger import get_logger


logger = get_logger(__name__)


def parse_roles_from_bulleted_response(response: str) -> List[Dict[str, str]]:
    """
    Parses an LLM-generated list of roles with two-sentence justifications.
    Handles common bullets (-, *, 1., •) and various delimiters (:, -, – , —).

    Returns:
        List of dicts: [{"title": ..., "justification": ...}, ...]
    """
    lines = response.strip().splitlines()

    # Match lines starting with a bullet character (including unicode dot •)
    bullet_lines = [
        line for line in lines
        if re.match(r"^(\s*[•\-\*\d]+\.\s+|\s*[•\-\*]\s+)", line.strip())
    ]

    parsed_roles = []
    for line in bullet_lines:
        # Remove bullet character (Unicode or ASCII)
        clean_line = re.sub(r"^(\s*[•\-\*\d]+\.\s+|\s*[•\-\*]\s+)", "", line).strip()

        # Split on first colon or dash-like delimiter
        split_match = re.split(r"\s*[:\-–—]\s+", clean_line, maxsplit=1)

        if len(split_match) == 2:
            title, justification = split_match
        else:
            title, justification = clean_line, ""

        parsed_roles.append({
            "title": title.strip(),
            "justification": justification.strip()
        })
    logger.info(f"Parsed roles: {parsed_roles}")
    return parsed_roles


def extract_json_block(text: str) -> Dict[str, Any]:
    """
    Extracts the first JSON object from a string and parses it into a Python dictionary.
    
    Args:
        text (str): The string that contains a JSON block somewhere within.
    
    Returns:
        dict: The parsed dictionary extracted from the first JSON object in the string.
    
    Raises:
        ValueError: If no valid JSON block is found or parsing fails.
    """
    try:
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON object found in input text.")
        json_str = json_match.group(0)
        logger.info(f"Parsed JSON: {json_str}")
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")


def return_value_from_response(response: str) -> str:
    logger.info(f"Response: {response}")
    return response.strip()