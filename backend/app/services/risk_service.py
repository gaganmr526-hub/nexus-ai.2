from sqlalchemy.orm import Session
from app.models.models import RiskFinding, Supplier
from app.graph.builder import build_graph, calculate_centrality, find_single_points_of_failure
import networkx as nx
from typing import Optional
import uuid
from datetime import datetime


def score_supplier_risk(supplier: Supplier, G: nx.DiGraph, centrality: dict) -> float:
    """Compute 0-1 risk score for a supplier node."""
    node_id = supplier.id
    bc = centrality.get("betweenness", {}).get(node_id, 0.0)
    in_deg = G.in_degree(node_id) if node_id in G else 0
    out_deg = G.out_degree(node_id) if node_id in G else 0
    tier_factor = max(0, (5 - supplier.tier_level) / 5)
    score = min(1.0, bc * 0.4 + (in_deg / max(len(G), 1)) * 0.3 + tier_factor * 0.2 + 0.1)
    return round(score, 4)


def build_risk_register(db: Session, company_id: str) -> list[RiskFinding]:
    return (
        db.query(RiskFinding)
        .filter(RiskFinding.company_id == company_id)
        .order_by(RiskFinding.created_at.desc())
        .all()
    )


def update_supplier_risk_scores(db: Session, company_id: str) -> int:
    G = build_graph(db, company_id=company_id)
    centrality = calculate_centrality(G)
    suppliers = (
        db.query(Supplier)
        .filter(Supplier.company_id == company_id)
        .all()
    )
    updated = 0
    for s in suppliers:
        new_score = score_supplier_risk(s, G, centrality)
        s.risk_score = new_score
        updated += 1
    db.commit()
    return updated


def detect_concentration_risk(db: Session, company_id: str) -> list[RiskFinding]:
    G = build_graph(db, company_id=company_id)
    spfs = find_single_points_of_failure(G)
    findings = []
    for spf in spfs[:10]:  # Top 10
        node_name = G.nodes[spf["node_id"]].get("name", spf["node_id"]) if spf["node_id"] in G else spf["node_id"]
        title = f"Single Point of Failure: {node_name}"
        existing = (
            db.query(RiskFinding)
            .filter(RiskFinding.company_id == company_id, RiskFinding.title == title)
            .first()
        )
        if not existing:
            finding = RiskFinding(
                id=str(uuid.uuid4()),
                company_id=company_id,
                finding_type="single_point_of_failure",
                title=title,
                description=f"Node '{node_name}' is a critical single point of failure with betweenness centrality {spf['betweenness_centrality']}.",
                severity="high" if spf["betweenness_centrality"] > 0.3 else "medium",
                status="open",
                confidence_score=min(1.0, spf["betweenness_centrality"] + 0.3),
                source_type="algorithm",
            )
            db.add(finding)
            db.flush()
            findings.append(finding)
    db.commit()
    return findings
