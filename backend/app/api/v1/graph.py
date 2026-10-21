from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User
from app.schemas.schemas import GraphData
from app.deps import get_current_user, require_company_access
from app.graph.builder import (
    get_graph_data, get_dependency_paths, calculate_centrality, build_graph,
    find_single_points_of_failure
)

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("")
def get_graph(
    company_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company_access(company_id, db, current_user)
    data = get_graph_data(db, company_id=company_id)
    return data


@router.get("/paths")
def graph_paths(
    from_id: str = Query(...),
    to_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    G = build_graph(db)
    paths = get_dependency_paths(G, from_id, to_id)
    return {"paths": paths, "path_count": len(paths)}


@router.get("/centrality")
def graph_centrality(
    company_id: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if company_id:
        require_company_access(company_id, db, current_user)
    G = build_graph(db, company_id=company_id)
    return calculate_centrality(G)


@router.get("/single-points-of-failure")
def spf(
    company_id: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if company_id:
        require_company_access(company_id, db, current_user)
    G = build_graph(db, company_id=company_id)
    return find_single_points_of_failure(G)
