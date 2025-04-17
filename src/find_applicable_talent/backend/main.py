from __future__ import annotations

from fastapi import FastAPI, Depends, HTTPException, Query, status, Body, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, TypeAdapter
from typing import List, Optional, Union
from threading import RLock

from find_applicable_talent.backend.candidates import CandidateList, Candidate
from find_applicable_talent.backend.util.logger import get_logger
from find_applicable_talent.backend import DATA_PATH

logger = get_logger(__name__)

app = FastAPI(title="Candidate API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

app.state.lock = RLock()  
app.state.candidates = CandidateList(path_to_submissions=str(DATA_PATH))

class FilterSpec(BaseModel):
    path: str
    operator: str
    value: Union[str, int, float, bool]


FilterSpecList = TypeAdapter(List[FilterSpec])          


def get_store() -> CandidateList:
    return app.state.candidates


@app.get("/candidates", response_model=list[Candidate], status_code=status.HTTP_200_OK)
def list_candidates(
    path: Optional[str] = Query(None),
    operator: Optional[str] = Query(None),
    value: Optional[str] = Query(None),
    fresh: bool = Query(False, alias="from_fresh_candidates"),
    store: CandidateList = Depends(get_store),
):
    logger.info(f"Listing candidates with path: {path}, operator: {operator}, value: {value}, fresh: {fresh}")
    logger.info(f"Have {len(store.candidates)} candidates")
    if all(p is not None for p in (path, operator, value)):
        spec = [{"path": path, "operator": operator, "value": value}]
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
    # hot‑swap the in‑memory index atomically
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