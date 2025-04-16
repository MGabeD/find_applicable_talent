from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import os


from candidates import Candidate, CANDIDATE_LIST


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/candidates")
def get_candidates():
    return CANDIDATE_LIST.get_candidates()

@app.get("/candidates/defaultFilters")
def get_default_filters():
    return {
        
    }



