import copy
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel
from typing import Optional, List, Dict
from find_applicable_talent.core.candidate import Candidate
from find_applicable_talent.util.logger import get_logger
from find_applicable_talent.reasoning_interface.model_interfaces import get_model
from find_applicable_talent.reasoning_interface.formatters import run_prompt_with_parser
from find_applicable_talent.reasoning_interface.formatters.prompt_builders import build_candidate_round_robin_prompt, build_role_refinement_prompt, build_role_ideation_prompt, build_candidate_criteria_prompt
from find_applicable_talent.reasoning_interface.formatters.response_parsers import extract_json_block, parse_roles_from_bulleted_response, return_value_from_response


logger = get_logger(__name__)


MAX_RETRIES = 3
MAX_WORKERS_PER_ROLE = 5
MAX_ROLE_WORKERS = 5
BATCH_SIZE = 6


class Role(BaseModel):
    title: Optional[str] = None
    justification: Optional[str] = None
    rubric: Optional[str] = None
    available_candidates: Dict[str, Optional[str]] = {}
    failed_ids: List[str] = []

    @classmethod
    def from_candidate_ids(cls, candidate_ids: List[str]):
        return cls(available_candidates={c: None for c in candidate_ids})

    def reset_candidates(self, available_candidates: List[str]):
        self.available_candidates = {c: None for c in available_candidates}
        self.failed_ids = []

    def fail_candidate(self, candidate_id: str):
        self.failed_ids.append(candidate_id)
        del self.available_candidates[candidate_id]

    def remove_candidate(self, candidate_id: str):
        del self.available_candidates[candidate_id]

    def set_role(self, role: Dict[str, str]):
        self.title = role["title"]
        self.justification = role["justification"]
        self.rubric = role["rubric"]


class RecruitmentReasoner:
    def __init__(self, candidates: List[Candidate]):
        self.candidates = {c.id: copy.deepcopy(c) for c in candidates}
        self.roles = [Role.from_candidate_ids(list(self.candidates.keys())) for _ in range(5)]
        self.model = get_model()

    @property
    def tagged_candidates(self) -> List[Candidate]:
        tagged = {}
        for role in self.roles:
            for candidate_id, reason in role.available_candidates.items():
                if candidate_id not in tagged:
                    tagged[candidate_id] = copy.deepcopy(self.candidates[candidate_id])
                    tagged[candidate_id].reasoner_tags = []
                tagged[candidate_id].reasoner_tags.append({
                    "role": role.title,
                    "justification": role.justification,
                    "reason": reason
                })
        return list(tagged.values())
    
    def set_roles(self, roles: List[Dict[str, str]]):
        for i in range(len(roles)):
            self.roles[i].set_role(roles[i])
    

    async def round_robin_single_role(self, role: Role):
        logger.info(f"Running round robin assignment for role: {role.title or '[Unassigned Title]'}")

        candidate_ids = list(role.available_candidates.keys())
        candidate_batches = [
            candidate_ids[i:i + BATCH_SIZE] for i in range(0, len(candidate_ids), BATCH_SIZE)
        ]

        async def process_batch(batch_ids: List[str]):
            for attempt in range(MAX_RETRIES):
                try:
                    batch_candidates = [self.candidates[cid] for cid in batch_ids]
                    logger.info(f"Processing batch {[c.id for c in batch_candidates]} (attempt {attempt+1})")
                    result = await run_prompt_with_parser(
                        build_candidate_round_robin_prompt,
                        extract_json_block,
                        self.model,
                        {"title": role.title, "justification": role.justification},
                        role.rubric,
                        batch_candidates
                    )
                    selected_id = result.get("selected_user_id")
                    explanation = result.get("explanation", "")
                    if selected_id in batch_ids:
                        role.available_candidates[selected_id] = explanation
                        for cid in batch_ids:
                            if cid != selected_id:
                                role.remove_candidate(cid)
                        return
                    else:
                        logger.warning(f"Selected ID {selected_id} not in batch.")
                except Exception as e:
                    logger.error(f"Error during batch process: {e}")
            logger.warning(f"Batch failed after {MAX_RETRIES} attempts.")
            for cid in batch_ids:
                role.fail_candidate(cid)

        await asyncio.gather(*[process_batch(batch) for batch in candidate_batches])


    async def assign_all_via_round_robin(self):
        await asyncio.gather(*[self.round_robin_single_role(role) for role in self.roles])

    async def update_roles_with_criteria(self, input_roles: List[Dict[str, str]]) -> None:
        if len(input_roles) != len(self.roles):
            raise ValueError("Input roles and roles must be the same length")

        async def generate_and_update(index: int, role: Dict[str, str]):
            if role["title"] and role["justification"]:
                logger.info(f"Generating rubric for role: {role['title']}")
                rubric = await run_prompt_with_parser(
                    build_candidate_criteria_prompt,
                    return_value_from_response,
                    self.model,
                    f"Title: {role['title']}\nJustification: {role['justification']}"
                )
                return index, role["title"], role["justification"], rubric
            else:
                logger.warning(f"Skipping rubric generation for incomplete role: {role}")
                return index, None, None, None

        results = await asyncio.gather(*[generate_and_update(i, role) for i, role in enumerate(input_roles)])

        for index, title, justification, rubric in results:
            if title and justification and rubric:
                self.roles[index].title = title
                self.roles[index].justification = justification
                self.roles[index].rubric = rubric

    def delete_candidate(self, candidate_id: str):
        for role in self.roles:
            role.remove_candidate(candidate_id)
        del self.candidates[candidate_id]


async def define_initial_roles(user_context: str) -> List[Dict[str, str]]:
    model = get_model()
    response = await run_prompt_with_parser(
        build_role_ideation_prompt,
        parse_roles_from_bulleted_response,
        model,
        user_context
    )
    logger.info(f"Defined roles: {response}")
    return response


async def refine_roles(current_roles: List[Dict[str, str]], user_feedback: str) -> List[Dict[str, str]]:
    model = get_model()
    logger.info(f"Refining roles with feedback: {user_feedback}")
    response = await run_prompt_with_parser(
        build_role_refinement_prompt,
        parse_roles_from_bulleted_response,
        model,
        current_roles,
        user_feedback
    )
    logger.info(f"Refined roles: {response}")
    return response
