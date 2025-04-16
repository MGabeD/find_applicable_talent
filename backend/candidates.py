from typing import List, Dict, Optional, Union, Callable
from pydantic import BaseModel
from datetime import datetime
import json
import os
import re
from dynamic_candidate_filter import build_filter_functions

class WorkExperience(BaseModel):
    company_name: Optional[str] = None
    roleName: Optional[str] = None

    # Note: your JSON has "company" not "company_name".
    # We'll accept both names in the constructor below.
    def __init__(self, **data):
        # If "company" is present in data, rename to "company_name"
        if 'company' in data:
            data['company_name'] = data.pop('company')
        super().__init__(**data)


class Degree(BaseModel):
    degree: Optional[str] = None
    subject: Optional[str] = None
    school: Optional[str] = None
    gpa: Optional[float] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    originalSchool: Optional[str] = None
    isTop50: bool = False

    def __init__(self, **data):
        # Parse gpa from string if needed
        gpa_value = data.get('gpa', None)
        if isinstance(gpa_value, str):
            # Example: "GPA 3.0-3.4" → we want 3.4
            matches = re.findall(r'\d+\.\d+', gpa_value)
            # If we got floats, take the last one
            if matches:
                data['gpa'] = float(matches[-1])  # last match
            else:
                data['gpa'] = None

        start = data.get('startDate', None)
        end = data.get('endDate', None)

        # Handle startDate
        if isinstance(start, str):
            start_str = start.strip().lower()
            if start_str == "present":
                data['startDate'] = None
            else:
                # Attempt to parse as a year
                try:
                    data['startDate'] = datetime(int(start_str), 1, 1)
                except ValueError:
                    data['startDate'] = None

        # Handle endDate
        if isinstance(end, str):
            end_str = end.strip().lower()
            if end_str == "present":
                data['endDate'] = None
            else:
                # Attempt to parse as a year
                try:
                    data['endDate'] = datetime(int(end_str), 1, 1)
                except ValueError:
                    data['endDate'] = None

        super().__init__(**data)

class Education(BaseModel):
    highest_level: Optional[str] = None
    degrees: Optional[List[Degree]] = None

class Candidate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    submitted_at: Optional[datetime] = None
    work_availability: Optional[List[str]] = None
    annual_salary_expectation: Optional[Dict[str, Union[int, str]]] = None
    work_experiences: Optional[List[WorkExperience]] = None
    education: Optional[Education] = None
    skills: Optional[List[str]] = None

    def __init__(self, **data):
        # If there's a date-like field for submitted_at, parse it
        submitted_at_value = data.get('submitted_at', None)
        if isinstance(submitted_at_value, str):
            data['submitted_at'] = datetime.strptime(
                submitted_at_value, "%Y-%m-%d %H:%M:%S.%f"
            )
        super().__init__(**data)


class CandidateList:
    def __init__(self, path_to_submissions: str):
        self.path_to_submissions = path_to_submissions
        self.candidates = []

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

# MARK: MAYBE illegal tot have this one
            # # 2. Must not have graduated before 2010
            # if latest_grad_year < 2010:
            #     continue

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
    
    def dynamic_simple_filters(self, filter_function: Callable[[Candidate], bool], inplace:bool = True) -> List[Candidate]:
        res = [candidate for candidate in self.candidates if filter_function(candidate)]
        if inplace:
            self.candidates = res
        return res
    
    def dynamic_filters(self, filter_spec_list: List[dict]) -> List[Candidate]:
        filter_funcs = []
        for spec in filter_spec_list:
            f = build_filter_functions(
                path=spec['path'],
                operator_key=spec['operator'],
                target_value=spec['value']
            )
            filter_funcs.append(f)

        def pass_all_filters(candidate) -> bool:
            return all(f(candidate) for f in filter_funcs)

        return [c for c in self.candidates if pass_all_filters(c)]

    def get_candidates(self) -> List[Candidate]:
        return self.candidates



    


CANDIDATE_LIST = CandidateList(path_to_submissions="data/data.json")
if __name__ == "__main__":
    print(len(CANDIDATE_LIST.candidates))
    filter_spec = {
        "path": "location",
        "operator": "==",
        "value": "Philadelphia"
    }

    matching_candidates = CANDIDATE_LIST.dynamic_filters([filter_spec])
    print(len(matching_candidates))
