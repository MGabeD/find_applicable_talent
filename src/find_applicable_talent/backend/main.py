from fastapi import FastAPI, Body, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Union
import json
import os
from threading import Lock

from util.logger import get_logger
from candidates import Candidate, CANDIDATE_LIST, DATA_PATH

logger = get_logger(__name__)


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class FilterSpec(BaseModel):
    path: str
    operator: str
    value: Union[str, int, float, bool]


def _to_dict(obj):
    return obj.dict()


@app.get("/candidates")
def get_candidates(
    path: str | None = Query(None),
    operator: str | None = Query(None),
    value: str | None = Query(None),
    from_fresh_candidates: bool = Query(False),
):
    if all(v is not None for v in [path, operator, value]):
        try:
            return CANDIDATE_LIST.dynamic_filters(filter_spec_list=[{"path": path, "operator": operator, "value": value}], from_fresh_candidates=from_fresh_candidates)
        except Exception as e:
            return {"error": str(e)}
    else:
        return CANDIDATE_LIST.get_candidates()


@app.post("/candidates/filter")
def post_candidates_filter(filter_spec: List[FilterSpec], from_fresh_candidates: bool = Query(False)):
    try:
        return CANDIDATE_LIST.dynamic_filters(filter_spec_list=filter_spec, from_fresh_candidates=from_fresh_candidates)
    except Exception as e:
        return {"error": str(e)}


@app.post("/candidates/reload")
def reload_candidates(path_to_submissions: Optional[str] = None):
    if path_to_submissions is None:
        path_to_submissions = str(DATA_PATH)
    CANDIDATE_LIST.reload_candidates(path_to_submissions=path_to_submissions)
    return {"message": "Candidates reloaded"}


@app.get("/candidates/{candidate_id}")
def get_candidate(candidate_id: str):
    cand = CANDIDATE_LIST.get_candidate_by_id(candidate_id)
    if cand is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return _to_dict(cand)


@app.delete("/candidates/{candidate_id}")
def delete_candidate(candidate_id: str):
    with _lock:
        ok = CANDIDATE_LIST.remove_candidate_by_id(candidate_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return {"status": "removed"}