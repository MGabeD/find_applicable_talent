from __future__ import annotations
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Query, status, Body, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, TypeAdapter
from typing import List, Optional, Union, Dict
from threading import RLock
from dotenv import load_dotenv
from find_applicable_talent.core.candidate_list import CandidateList
from find_applicable_talent.core.candidate import Candidate
from find_applicable_talent.util.logger import get_logger
from find_applicable_talent.core import DATA_PATH
from find_applicable_talent.core.round_robin_candidates import define_initial_roles, refine_roles
import asyncio
from contextlib import asynccontextmanager


load_dotenv()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.async_lock = asyncio.Lock()
    app.state.lock = RLock()
    app.state.candidates = CandidateList(path_to_submissions=str(DATA_PATH))
    
    yield  


app = FastAPI(title="Candidate API", version="0.1.0", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


class FilterSpec(BaseModel):
    path: str
    operator: str
    value: Union[str, int, float, bool, datetime]
    invert: bool = False


FilterSpecList = TypeAdapter(List[FilterSpec])          


def get_store() -> CandidateList:
    return app.state.candidates


@app.get("/candidates", response_model=list[Candidate], status_code=status.HTTP_200_OK)
def list_candidates(
    path: Optional[str] = Query(None),
    operator: Optional[str] = Query(None),
    value: Optional[str] = Query(None),
    invert: Optional[bool] = Query(False),
    fresh: bool = Query(False, alias="from_fresh_candidates"),
    store: CandidateList = Depends(get_store),
):
    logger.info(f"Listing candidates with path: {path}, operator: {operator}, value: {value}, fresh: {fresh}")
    logger.info(f"Have {len(store.candidates)} candidates")
    if all(p is not None for p in (path, operator, value)):
        spec = [{"path": path, "operator": operator, "value": value, "invert": invert}]
        logger.info(f"Filtering candidates with spec: {spec}")
        data = store.dynamic_filters(spec, from_fresh_candidates=fresh)
        logger.info(f"Have {len(data)} candidates after filtering")
        return data
    if fresh:
        return store.get_candidates()
    else:
        return store.get_filtered_candidates()


@app.post("/candidates/filter", response_model=list[Candidate])
def list_filtered_candidates(
    specs: list[FilterSpec], fresh: bool = Query(True, alias="from_fresh_candidates"),
    store: CandidateList = Depends(get_store),
):
    logger.info(f"Filtering candidates with specs: {specs}")
    return store.dynamic_filters([s.model_dump() for s in specs], from_fresh_candidates=fresh)


@app.get("/candidates/{candidate_id}", response_model=Candidate)
def get_candidate(candidate_id: str, store: CandidateList = Depends(get_store)):
    cand = store.get_candidate_by_id(candidate_id)
    if cand is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return cand


@app.delete("/candidates/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_candidate(candidate_id: str, store: CandidateList = Depends(get_store)):
    with app.state.lock:
        if not store.remove_candidate_by_id(candidate_id):
            raise HTTPException(status_code=404, detail="Candidate not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/candidates/reload", status_code=status.HTTP_202_ACCEPTED)
def reload_candidates(path: Optional[str] = Body(None, embed=True)):
    with app.state.lock:
        app.state.candidates = CandidateList(path_to_submissions=path or str(DATA_PATH))
    return {"detail": "candidates reloaded"}

@app.post("/candidates/selected/{candidate_id}", status_code=status.HTTP_200_OK)
def select_candidate(
    candidate_id: str,
    store: CandidateList = Depends(get_store)
):
    logger.info(f"Selecting candidate by ID {candidate_id}")
    with app.state.lock:
        if not store.select_candidate_by_id(candidate_id):
            raise HTTPException(404, "Candidate not found")
    return {"detail": f"Candidate {candidate_id} selected successfully"}

@app.delete("/candidates/selected/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_selected_candidate(
    candidate_id: str,
    store: CandidateList = Depends(get_store)
):
    logger.info(f"Removing candidate by ID {candidate_id}")
    with app.state.lock:
        if not store.remove_selected_candidate_by_id(candidate_id):
            raise HTTPException(404, "Candidate not in selected list")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.get("/candidates/selected/", response_model=List[Candidate])
def list_selected_candidates(store: CandidateList = Depends(get_store)):
    logger.info(f"Listing selected candidates")
    return store.get_selected_candidates()

# REASONER

@app.post("/candidates/reasoner/load", status_code=status.HTTP_202_ACCEPTED)
def load_reasoner(store: CandidateList = Depends(get_store)):
    """
    Load the RecruitmentReasoner using selected candidates if any, otherwise from all candidates.
    """
    with app.state.lock:
        store.load_reasoner()
        tagged_candidates = store.get_tagged_candidates()
    return {"detail": "Reasoner initialized successfully.", "tagged_candidates": tagged_candidates}

@app.post("/candidates/reasoner/reset", status_code=status.HTTP_202_ACCEPTED)
def reset_reasoner(store: CandidateList = Depends(get_store)):
    """
    Reset the RecruitmentReasoner and reload candidates.
    """
    with app.state.lock:
        store.reset_reasoner()
    return {"detail": "Reasoner reset successfully."}

@app.get("/candidates/reasoner/tagged", response_model=List[Candidate])
def get_tagged_candidates(store: CandidateList = Depends(get_store)):
    """
    Return tagged candidates with reasoner annotations.
    """
    if store.round_robin_candidates is None:
        raise HTTPException(400, "Reasoner has not been initialized. Call /candidates/reasoner/load first.")
    return store.get_tagged_candidates()

@app.post("/candidates/reasoner/set_filtered", status_code=202)
def set_filtered_candidates_from_reasoner(store: CandidateList = Depends(get_store)):
    """
    Set filtered candidates list based on current tagged candidates.
    """
    if store.round_robin_candidates is None:
        raise HTTPException(400, "Reasoner has not been initialized. Call /candidates/reasoner/load first.")
    with app.state.lock:
        store.set_filtered_candidates_from_reasoner()

class RoleDefinitionRequest(BaseModel):
    user_context: str

class RoleRefinementRequest(BaseModel):
    current_roles: List[Dict[str, str]]
    user_feedback: str

@app.post("/candidates/reasoner/define_roles", status_code=200)
async def api_define_roles(payload: RoleDefinitionRequest):
    """
    Define initial roles using the user context string.
    """
    try:
        logger.info(f"Defining roles with user context: {payload.user_context}")
        roles = await define_initial_roles(payload.user_context)
        return {"roles": roles}
    except Exception as e:
        logger.error(f"Failed to define roles: {e}")
        raise HTTPException(status_code=500, detail="Failed to define initial roles")

@app.post("/candidates/reasoner/refine_roles", status_code=200)
async def api_refine_roles(payload: RoleRefinementRequest):
    """
    Refine roles using user feedback and current role definitions.
    """
    try:
        refined_roles = await refine_roles(payload.current_roles, payload.user_feedback)
        logger.info(f"Refined roles: {refined_roles}")
        return {"roles": refined_roles}
    except Exception as e:
        logger.error(f"Failed to refine roles: {e}")
        raise HTTPException(status_code=500, detail="Failed to refine roles")
    

class RoleInput(BaseModel):
    title: str
    justification: str

class RoleCriteriaRequest(BaseModel):
    roles: List[RoleInput]

@app.post("/candidates/reasoner/update_roles_with_criteria", status_code=200)
async def api_update_roles_with_criteria(payload: RoleCriteriaRequest, store: CandidateList = Depends(get_store)):
    """
    Update existing roles with new title/justification and generate rubrics concurrently.
    """
    try:
        input_roles = [{"title": r.title, "justification": r.justification} for r in payload.roles]
        if store.round_robin_candidates is None:
            raise HTTPException(400, "Reasoner has not been initialized. Call /candidates/reasoner/load first.")
        
        async with app.state.async_lock:
            await store.round_robin_candidates.update_roles_with_criteria(input_roles)

        return {"message": "Roles updated successfully"}
    except Exception as e:
        logger.error(f"Failed to update roles with criteria: {e}")
        raise HTTPException(status_code=500, detail="Failed to update roles with criteria")
    
@app.get("/candidates/reasoner/roles", response_model=List[Dict[str, str]])
def get_reasoner_roles(store: CandidateList = Depends(get_store)):
    """
    Return the current list of roles from the reasoner, including title, justification, and rubric.
    """
    return store.get_roles()
