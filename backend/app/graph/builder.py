import networkx as nx
from sqlalchemy.orm import Session
from typing import Optional
from app.models.models import Supplier, SupplierRelationship, Company


def build_graph(
    db: Session,
    company_id: Optional[str] = None,
    authorized_company_ids: Optional[list[str]] = None,
) -> nx.DiGraph:
    """Build NetworkX DiGraph from SupplierRelationship records."""
    G = nx.DiGraph()

    # Load suppliers
    q = db.query(Supplier)
    if company_id:
        q = q.filter(Supplier.company_id == company_id)
    elif authorized_company_ids is not None:
        q = q.filter(Supplier.company_id.in_(authorized_company_ids))
    suppliers = q.all()

    for s in suppliers:
        G.add_node(
            s.id,
            name=s.name,
            supplier_type=s.supplier_type,
            tier_level=s.tier_level,
            risk_score=s.risk_score or 0.0,
            criticality=s.criticality or "medium",
            geographic_region=s.geographic_region or "Unknown",
            company_id=s.company_id,
            verification_status=s.verification_status or "unverified",
        )

    # Load relationships
    supplier_ids = {s.id for s in suppliers}
    rels = db.query(SupplierRelationship).all()
    for r in rels:
        if r.from_supplier_id in supplier_ids or r.to_supplier_id in supplier_ids:
            # Ensure both nodes exist
            if r.from_supplier_id not in G:
                _add_missing_node(db, G, r.from_supplier_id)
            if r.to_supplier_id not in G:
                _add_missing_node(db, G, r.to_supplier_id)
            G.add_edge(
                r.from_supplier_id,
                r.to_supplier_id,
                id=r.id,
                relationship_type=r.relationship_type,
                confidence_score=r.confidence_score or 0.5,
                verification_status=r.verification_status,
            )

    return G


def _add_missing_node(db: Session, G: nx.DiGraph, supplier_id: str) -> None:
    s = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if s:
        G.add_node(
            s.id,
            name=s.name,
            supplier_type=s.supplier_type,
            tier_level=s.tier_level,
            risk_score=s.risk_score or 0.0,
            criticality=s.criticality or "medium",
            geographic_region=s.geographic_region or "Unknown",
            company_id=s.company_id,
            verification_status=s.verification_status or "unverified",
        )


def get_graph_data(db: Session, company_id: str, authorized_company_ids: Optional[list[str]] = None) -> dict:
    G = build_graph(db, company_id=company_id, authorized_company_ids=authorized_company_ids)
    nodes = []
    for node_id, attrs in G.nodes(data=True):
        nodes.append({
            "id": node_id,
            "label": attrs.get("name", node_id),
            "supplier_type": attrs.get("supplier_type", "direct"),
            "tier_level": attrs.get("tier_level", 1),
            "risk_score": attrs.get("risk_score"),
            "criticality": attrs.get("criticality"),
            "geographic_region": attrs.get("geographic_region"),
            "company_id": attrs.get("company_id", ""),
        })
    edges = []
    for u, v, attrs in G.edges(data=True):
        edges.append({
            "id": attrs.get("id", f"{u}-{v}"),
            "source": u,
            "target": v,
            "relationship_type": attrs.get("relationship_type", "supplies"),
            "confidence_score": attrs.get("confidence_score"),
            "verification_status": attrs.get("verification_status", "unverified"),
        })
    return {"nodes": nodes, "edges": edges}


def find_single_points_of_failure(G: nx.DiGraph) -> list[dict]:
    """Nodes whose removal disconnects the graph or significantly reduces reachability."""
    spfs = []
    if len(G.nodes) == 0:
        return spfs

    # Use articulation points on undirected version
    undirected = G.to_undirected()
    try:
        art_points = set(nx.articulation_points(undirected))
    except Exception:
        art_points = set()

    centrality = nx.betweenness_centrality(G)

    for node in G.nodes:
        attrs = G.nodes[node]
        is_art = node in art_points
        bc = centrality.get(node, 0)
        in_deg = G.in_degree(node)
        out_deg = G.out_degree(node)

        if is_art or bc > 0.1 or (in_deg >= 2 and out_deg >= 2):
            spfs.append({
                "node_id": node,
                "name": attrs.get("name", node),
                "is_articulation_point": is_art,
                "betweenness_centrality": round(bc, 4),
                "in_degree": in_deg,
                "out_degree": out_deg,
                "supplier_type": attrs.get("supplier_type"),
                "geographic_region": attrs.get("geographic_region"),
            })

    spfs.sort(key=lambda x: x["betweenness_centrality"], reverse=True)
    return spfs


def get_dependency_paths(G: nx.DiGraph, from_id: str, to_id: str) -> list[list[str]]:
    """Return all simple paths between two nodes."""
    if from_id not in G or to_id not in G:
        return []
    try:
        return list(nx.all_simple_paths(G, from_id, to_id, cutoff=8))
    except nx.NetworkXNoPath:
        return []
    except Exception:
        return []


def get_upstream_ancestors(G: nx.DiGraph, node_id: str) -> list[str]:
    """
    Return all upstream suppliers of node_id.
    Edge direction: A → B means A depends on B (B is upstream of A).
    So upstream nodes of A = nx.descendants(G, A) = nodes reachable following edges forward.
    """
    if node_id not in G:
        return []
    return list(nx.descendants(G, node_id))


def get_downstream_descendants(G: nx.DiGraph, node_id: str) -> list[str]:
    """
    Return all downstream buyers/dependents of node_id.
    Edge direction: A → B means A depends on B.
    So downstream dependents of B = nodes that eventually point to B = nx.ancestors(G, B).
    For a supplier node, we also return descendants for graph traversal purposes.
    """
    if node_id not in G:
        return []
    # descendants in directed graph = nodes reachable from node_id
    return list(nx.descendants(G, node_id))


def calculate_centrality(G: nx.DiGraph) -> dict:
    if len(G.nodes) == 0:
        return {"betweenness": {}, "in_degree": {}, "out_degree": {}, "pagerank": {}}
    bc = nx.betweenness_centrality(G)
    in_deg = dict(G.in_degree())
    out_deg = dict(G.out_degree())
    try:
        pr = nx.pagerank(G, max_iter=200)
    except Exception:
        pr = {n: 0.0 for n in G.nodes}
    return {
        "betweenness": {k: round(v, 6) for k, v in bc.items()},
        "in_degree": {k: float(v) for k, v in in_deg.items()},
        "out_degree": {k: float(v) for k, v in out_deg.items()},
        "pagerank": {k: round(v, 6) for k, v in pr.items()},
    }
