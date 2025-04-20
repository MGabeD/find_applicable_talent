from typing import Optional, List, Dict, Union
from pydantic import BaseModel
from datetime import datetime
import json
import uuid
import re


class WorkExperience(BaseModel):
    company: Optional[str] = None
    roleName: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)

    def to_llm_dict(self) -> dict:
        return {
            "company": self.company or "",
            "roleName": self.roleName or ""
        }
    
    def __str__(self) -> str:
        return json.dumps(self.to_llm_dict(), separators=(',', ':'))


class Degree(BaseModel):
    degree: Optional[str] = None
    subject: Optional[str] = None
    school: Optional[str] = None
    gpa: Optional[float] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    originalSchool: Optional[str] = None
    isTop50: bool = False
    isTop25: bool = False

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

    def to_llm_dict(self) -> dict:
        return {
            "degree": self.degree or "",
            "subject": self.subject or "",
            "school": self.school or "",
            "gpa": self.gpa if self.gpa is not None else ""
        }
    
    def __str__(self) -> str:
        return json.dumps(self.to_llm_dict(), separators=(',', ':'))


class Education(BaseModel):
    highest_level: Optional[str] = None
    degrees: Optional[List[Degree]] = None
    most_recent_end_date: Optional[datetime] = None
    most_recent_gpa: Optional[float] = None

    def __init__(self, **data):
        raw_degrees = data.get("degrees", [])
        degree_objs = [d if isinstance(d, Degree) else Degree(**d) for d in raw_degrees]
        
        most_recent_end = None
        most_recent_gpa = None

        if degree_objs:
            # Sort by endDate descending, treating None as datetime.min
            sorted_degrees = sorted(
                degree_objs,
                key=lambda d: d.endDate or datetime.min,
                reverse=True
            )
            for deg in sorted_degrees:
                if not most_recent_end and deg.endDate:
                    most_recent_end = deg.endDate
                if not most_recent_gpa and deg.gpa is not None:
                    most_recent_gpa = deg.gpa
                if most_recent_end and most_recent_gpa:
                    break

        data['degrees'] = degree_objs
        data['most_recent_end_date'] = most_recent_end
        data['most_recent_gpa'] = most_recent_gpa

        super().__init__(**data)

    def to_llm_dict(self) -> dict:
        return {
            "highest_level": self.highest_level or "",
            "degrees": [{**self.degrees[i].to_llm_dict(), "idx": i} for i in range(0, len(self.degrees))] if self.degrees else [],
            "most_recent_end_date": self.most_recent_end_date.isoformat() if self.most_recent_end_date else "",
            "most_recent_gpa": self.most_recent_gpa or ""
        }
    
    def __str__(self) -> str:
        return json.dumps(self.to_llm_dict(), separators=(',', ':'))


class Candidate(BaseModel):
    id: str
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
    reasoner_tags: Optional[List[Dict[str, str]]] = None

    def __init__(self, **data):
        # Generate a unique ID if one isn't provided
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
            
        # If there's a date-like field for submitted_at, parse it
        submitted_at_value = data.get('submitted_at', None)
        if isinstance(submitted_at_value, str):
            data['submitted_at'] = datetime.strptime(
                submitted_at_value, "%Y-%m-%d %H:%M:%S.%f"
            )
        super().__init__(**data)

    def to_llm_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name or "",
            "email": self.email or "",
            "phone": self.phone or "",
            "location": self.location or "",
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else "",
            "work_availability": self.work_availability or [],
            "annual_salary_expectation": self.annual_salary_expectation or {},
            "work_experiences": [{**we.to_llm_dict(), "idx": i} for i, we in enumerate(self.work_experiences)] if self.work_experiences else [],
            "education": self.education.to_llm_dict() if self.education else {},
            "skills": self.skills or []
        }
    
    def __str__(self) -> str:
        return json.dumps(self.to_llm_dict(), separators=(',', ':'))