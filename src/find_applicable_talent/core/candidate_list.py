from typing import List, Dict, Optional, Callable
import copy
import json
from find_applicable_talent.util.logger import get_logger
from find_applicable_talent.core.round_robin_candidates import RecruitmentReasoner
from find_applicable_talent.core.candidate import Candidate
from find_applicable_talent.core.dynamic_candidate_filter import build_filter_functions
from find_applicable_talent.core import DATA_PATH


logger = get_logger(__name__)


class CandidateList:
    def __init__(self, path_to_submissions: str = str(DATA_PATH)):
        self.path_to_submissions = path_to_submissions
        self.candidates = []
        self.selected_candidates = []
        self.filtered_candidates = []
        self._load_candidates()
        self.filtered_candidates = self.candidates.copy()
        self.round_robin_candidates = None

    def _load_candidates(self):
        with open(self.path_to_submissions, 'r') as f:
            submissions = json.load(f)

        # Load candidates while ignoring any invalid entries
        raw_candidates = []
        for submission in submissions:
            try:
                candidate = Candidate(**submission)
                raw_candidates.append(candidate)
            except Exception as e:
                print(f"Error: {e} - discarding submission: {submission}")

        # Now filter them according to your rules
        self.candidates = self._filter_candidates(raw_candidates)

    def _filter_candidates(self, candidates: List[Candidate]) -> List[Candidate]:
        filtered = []

        for c in candidates:
            # 1. Must have at least one degree
            if not c.education or not c.education.degrees or len(c.education.degrees) < 1:
                continue

            # Find the latest numeric endDate among the degrees
            # (ignore any 'endDate' that is None or "Present")
            numeric_end_dates = []
            for d in c.education.degrees:
                if d.endDate is not None:  # present => None
                    numeric_end_dates.append(d.endDate.year)

            # If there's no numeric endDate, we can't confirm they graduated
            if not numeric_end_dates:
                continue

            latest_grad_year = max(numeric_end_dates)

            if latest_grad_year < 2000:
                continue

            # 3. Must not have more than 10 total jobs
            jobs_count = 0
            if c.work_experiences:
                jobs_count = len(c.work_experiences)

            if jobs_count > 10:
                continue

            # 4. Must not have more than 1 job per year post-college
            # i.e. (2025 - latest_grad_year) / jobs_count > 1
            # => 2025 - latest_grad_year > jobs_count
            # We handle the case of jobs_count = 0 separately (allow?).
            if jobs_count > 0:
                years_since_grad = 2025 - latest_grad_year
                if years_since_grad <= jobs_count:  # means ratio <= 1
                    continue

            filtered.append(c)

        return filtered
    
    def reload_candidates(self, path_to_submissions: str = str(DATA_PATH)):
        self.path_to_submissions = path_to_submissions
        self.candidates = []
        self.selected_candidates = []
        self.filtered_candidates = []
        self._load_candidates()
        self.filtered_candidates = self.candidates.copy()

    def dynamic_simple_filters(self, filter_function: Callable[[Candidate], bool], inplace:bool = True) -> List[Candidate]:
        res = [candidate for candidate in self.candidates if filter_function(candidate)]
        if inplace:
            self.candidates = res
        return res
    
    def dynamic_filters(self, filter_spec_list: List[dict], from_fresh_candidates: bool = True) -> List[Candidate]:
        filter_funcs = []
        for spec in filter_spec_list:
            f = build_filter_functions(
                path=spec['path'],
                operator_key=spec['operator'],
                target_value=spec['value'],
                invert=spec['invert']
            )
            filter_funcs.append(f)

        def pass_all_filters(candidate) -> bool:
            return all(f(candidate) for f in filter_funcs)
        
        if from_fresh_candidates:
            self.filtered_candidates = [c for c in self.candidates if pass_all_filters(c)]
        else:
            self.filtered_candidates = [c for c in self.filtered_candidates if pass_all_filters(c)]

        return self.filtered_candidates
    
    def get_candidates(self) -> List[Candidate]:
        return self.candidates
    
    def get_filtered_candidates(self) -> List[Candidate]:
        return self.filtered_candidates

    def get_candidate_by_id(self, candidate_id: str) -> Optional[Candidate]:
        for candidate in self.candidates:
            if candidate.id == candidate_id:
                return candidate    
        return None
    
    def remove_candidate_by_id(self, candidate_id: str) -> bool:
        for candidate in self.filtered_candidates:
            if candidate.id == candidate_id:
                self.filtered_candidates.remove(candidate)

        if self.round_robin_candidates is not None:
            if candidate_id in self.round_robin_candidates.available_candidates:
                logger.info(f"Removing candidate {candidate_id} from round robin candidates")
                del self.round_robin_candidates.available_candidates[candidate_id]

        for candidate in self.candidates:
            if candidate.id == candidate_id:
                self.candidates.remove(candidate)
                return True
        return False

    def select_candidate_by_id(self, candidate_id: str) -> bool:
        logger.info(f"Selecting candidate {candidate_id}")
        # logger.info(f"Have candidates: {self.candidates}")
        candidate = self.get_candidate_by_id(candidate_id)
        if candidate is None:
            return False
        for c in self.selected_candidates:
            if c.id == candidate_id:
                logger.info(f"Candidate {candidate_id} already in selected candidates")
                return True
            
        logger.info(f"Adding candidate {candidate.id} to selected candidates")
        self.selected_candidates.append(candidate)
        return True
    
    def remove_selected_candidate_by_id(self, candidate_id: str) -> bool:
        logger.info(f"Have selected candidates: { ', '.join(s.id for s in self.selected_candidates) }")  
        for candidate in self.selected_candidates:
            if candidate.id == candidate_id:
                self.selected_candidates.remove(candidate)
                return True
        return False

    def get_selected_candidates(self) -> List[Candidate]:
        logger.info(f"Have selected candidates: { ', '.join(s.id for s in self.selected_candidates) }")
        return self.selected_candidates

    # MARK: - Reasoner
    def load_reasoner(self):
        if len(self.selected_candidates) > 0:
            self.round_robin_candidates = RecruitmentReasoner(
                candidates=self.selected_candidates
            )
        else:
            self.round_robin_candidates = RecruitmentReasoner(
                candidates=self.candidates
            )

    def set_filtered_candidates_from_reasoner(self):
        self.filtered_candidates = copy.deepcopy(self.round_robin_candidates.tagged_candidates)

    def get_tagged_candidates(self) -> List[Candidate]:
        return self.round_robin_candidates.tagged_candidates

