import json
from collections import defaultdict
from typing import Optional
import networkx as nx
from rapidfuzz import fuzz
from sqlalchemy.orm import Session
from app.models.models import Supplier, RiskFinding, SupplierRelationship
from app.graph.builder import build_graph, get_dependency_paths, calculate_centrality
import uuid
from datetime import datetime


def fuzzy_match_entities(name: str, candidates: list[str], threshold: float = 80.0) -> list[str]:
    """Return candidates whose fuzzy ratio to `name` exceeds threshold."""
    return [c for c in candidates if fuzz.ratio(name.lower(), c.lower()) >= threshold]


def detect_shared_upstream_sources(
    G: nx.DiGraph, direct_supplier_ids: list[str]
) -> list[dict]:
    """
    For each pair of direct suppliers, find their common upstream nodes
    (nodes reachable by following the dependency edges forward from each supplier).

    Edge direction: A → B means "A depends_on/supplies_from B", so B is upstream of A.
    nx.descendants(G, A) gives nodes reachable from A following edges = upstream nodes of A.
    Returns list of dicts: {shared_node, affected_direct_suppliers, paths}.
    """
    shared: dict[str, dict] = {}

    # Build upstream set for each direct supplier
    upstream_map: dict[str, set] = {}
    for sup_id in direct_supplier_ids:
        if sup_id not in G:
            upstream_map[sup_id] = set()
            continue
        # descendants = nodes reachable from sup_id following directed edges = upstream suppliers
        upstream_map[sup_id] = set(nx.descendants(G, sup_id))
        upstream_map[sup_id].add(sup_id)

    for sup_id in direct_supplier_ids:
        for other_id in direct_supplier_ids:
            if other_id == sup_id:
                continue

            common = upstream_map.get(sup_id, set()) & upstream_map.get(other_id, set())
            # Exclude the direct suppliers themselves from shared nodes
            common -= set(direct_supplier_ids)

            for node in common:
                if node not in shared:
                    shared[node] = {
                        "shared_node": node,
                        "affected_direct_suppliers": set(),
                        "paths": {},
                    }
                shared[node]["affected_direct_suppliers"].add(sup_id)
                shared[node]["affected_direct_suppliers"].add(other_id)

    # Convert sets to lists and compute paths
    result = []
    for key, info in shared.items():
        affected = list(info["affected_direct_suppliers"])
        paths = {}
        for sup_id in affected:
            # Path from direct supplier → shared upstream node (following directed edges)
            p = get_dependency_paths(G, sup_id, info["shared_node"])
            if p:
                paths[sup_id] = p
        result.append({
            "shared_node": info["shared_node"],
            "affected_direct_suppliers": affected,
            "paths": paths,
        })

    return result


def calculate_concentration_risk(G: nx.DiGraph, node_id: str) -> float:
    """Score 0-1: how concentrated/central this node is."""
    if node_id not in G:
        return 0.0
    centrality = calculate_centrality(G)
    bc = centrality["betweenness"].get(node_id, 0.0)
    in_deg = centrality["in_degree"].get(node_id, 0.0)
    total_nodes = max(len(G.nodes), 1)
    # Normalise in-degree
    norm_in = in_deg / total_nodes
    return round(min(1.0, bc + norm_in), 4)


def discover_hidden_dependencies(
    db: Session,
    company_id: str,
    G: Optional[nx.DiGraph] = None,
) -> list[RiskFinding]:
    """
    Core algorithm:
    1. Find direct suppliers of company_id.
    2. Build/use graph.
    3. Find shared upstream ancestors for pairs of direct suppliers.
    4. Score and rank findings.
    5. Persist RiskFindings (upsert by title).
    6. Return list of RiskFinding ORM objects.
    """
    if G is None:
        G = build_graph(db)

    # Direct suppliers of the company
    direct_suppliers = (
        db.query(Supplier)
        .filter(Supplier.company_id == company_id, Supplier.tier_level == 1)
        .all()
    )
    direct_ids = [s.id for s in direct_suppliers]
    direct_name_map = {s.id: s.name for s in direct_suppliers}

    # All suppliers (for name map)
    all_suppliers = db.query(Supplier).all()
    all_name_map = {s.id: s.name for s in all_suppliers}

    shared = detect_shared_upstream_sources(G, direct_ids)

    # Score by number of affected direct suppliers + centrality
    centrality = calculate_centrality(G)

    findings = []
    for item in shared:
        node = item["shared_node"]
        affected = item["affected_direct_suppliers"]
        paths = item["paths"]

        if len(affected) < 2:
            continue

        node_name = all_name_map.get(node, node)
        affected_names = [all_name_map.get(sid, sid) for sid in affected]

        # Severity based on number of affected direct suppliers + centrality
        bc = centrality["betweenness"].get(node, 0.0)
        conc = calculate_concentration_risk(G, node)
        n_affected = len(affected)
        score = min(1.0, (n_affected / max(len(direct_ids), 1)) * 0.6 + bc * 0.3 + conc * 0.1)

        if score >= 0.7 or n_affected >= 3:
            severity = "critical"
        elif score >= 0.4 or n_affected >= 2:
            severity = "high"
        elif score >= 0.2:
            severity = "medium"
        else:
            severity = "low"

        title = f"Hidden Shared Dependency on {node_name}"
        description = (
            f"{n_affected} direct suppliers ({', '.join(affected_names)}) "
            f"all depend on upstream entity '{node_name}'. "
            f"A disruption at '{node_name}' could simultaneously impact all of them."
        )

        # Check if finding already exists
        existing = (
            db.query(RiskFinding)
            .filter(RiskFinding.company_id == company_id, RiskFinding.title == title)
            .first()
        )

        paths_serialisable = {k: v for k, v in paths.items()}

        if existing:
            existing.severity = severity
            existing.confidence_score = round(score, 4)
            existing.affected_suppliers_json = json.dumps(affected)
            existing.dependency_paths_json = json.dumps(paths_serialisable)
            existing.updated_at = datetime.utcnow()
            db.flush()
            findings.append(existing)
        else:
            # Get shared upstream supplier DB object
            shared_sup = db.query(Supplier).filter(Supplier.id == node).first()
            finding = RiskFinding(
                id=str(uuid.uuid4()),
                company_id=company_id,
                finding_type="hidden_dependency",
                title=title,
                description=description,
                shared_upstream_supplier_id=node if shared_sup else None,
                severity=severity,
                status="open",
                confidence_score=round(score, 4),
                affected_suppliers_json=json.dumps(affected),
                affected_products_json=json.dumps([]),
                dependency_paths_json=json.dumps(paths_serialisable),
                evidence_json=json.dumps({"betweenness": bc, "concentration": conc}),
                recommended_action=(
                    f"Dual-source components from '{node_name}' or "
                    f"qualify alternative upstream suppliers."
                ),
                source_type="algorithm",
            )
            db.add(finding)
            db.flush()
            findings.append(finding)

    db.commit()
    return findings
