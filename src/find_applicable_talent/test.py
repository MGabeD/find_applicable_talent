# from find_applicable_talent.reasoning_module.formatters.prompt_builders import build_role_ideation_prompt, build_candidate_criteria_prompt
# from find_applicable_talent.reasoning_module.formatters.response_parsers import parse_roles_from_bulleted_response,return_value_from_response, extract_json_block
# from find_applicable_talent.reasoning_module.model_interfaces import get_model
# from find_applicable_talent.reasoning_module.formatters import run_prompt_with_parser
# from find_applicable_talent.util.logger import get_logger
# from find_applicable_talent.backend.candidates import CandidateList
# from find_applicable_talent.backend import DATA_PATH
# from find_applicable_talent.reasoning_module.formatters.prompt_builders import build_candidate_round_robin_prompt


# logger = get_logger(__name__)


# model = get_model()
# role_context = "We are a startup that makes a product that helps companies find and hire the right talen based on ML models suggesions of good candidates"
# response = run_prompt_with_parser(build_role_ideation_prompt, parse_roles_from_bulleted_response, model, role_context)
# job_criteria = []
# for res in response[:2]:
#     logger.info(f"res: {res}")
# #     criteria = run_prompt_with_parser(build_candidate_criteria_prompt, return_value_from_response, model, res)
# #     logger.info(f"Criteria: {criteria}")
# #     job_criteria.append([res,criteria])

# # candidates = CandidateList(path_to_submissions=str(DATA_PATH))
# # current_round_robin = candidates.candidates[:6]
# # logger.info(f"Current round robin: {current_round_robin}")
# # choosen = run_prompt_with_parser(build_candidate_round_robin_prompt, extract_json_block, model, job_criteria[0][0], job_criteria[0][1], current_round_robin)
# # logger.info(f"Choosen: {choosen}")


from find_applicable_talent.core.round_robin_candidates import define_initial_roles, refine_roles

user_context = "We are a startup that makes a product that helps companies find and hire the right talen based on ML models suggesions of good candidates"
roles = define_initial_roles(user_context)
print(roles)

