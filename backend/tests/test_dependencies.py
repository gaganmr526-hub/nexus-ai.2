"""test_dependencies.py — Hidden dependency discovery tests.
Must find that CirroTech, Northstar, ArcLight, SkyNode share Helios upstream.
"""
import pytest
from app.services.dependency_service import (
    discover_hidden_dependencies,
    detect_shared_upstream_sources,
    fuzzy_match_entities,
)
from app.graph.builder import build_graph


def test_fuzzy_match_finds_helios():
    candidates = [
        "Helios Semiconductor Works",
        "Northstar Precision",
        "CirroTech Electronics",
    ]
    matches = fuzzy_match_entities("Helios Semiconductor", candidates, threshold=70)
    assert "Helios Semiconductor Works" in matches


def test_fuzzy_match_no_match():
    candidates = ["Northstar", "BluePeak", "CirroTech"]
    matches = fuzzy_match_entities("Helios Semiconductor", candidates, threshold=90)
    assert matches == []


def test_detect_shared_upstream(db, demo_company, helios_network, demo_membership):
    """detect_shared_upstream_sources must find Helios as common ancestor."""
    G = build_graph(db, company_id=demo_company.id)

    direct_ids = [
        helios_network["cirrotech"].id,
        helios_network["northstar"].id,
        helios_network["arclight"].id,
        helios_network["skynode"].id,
    ]

    shared = detect_shared_upstream_sources(G, direct_ids)

    # There should be at least one shared upstream node
    assert len(shared) > 0

    # Helios must be among the shared nodes
    shared_node_ids = {item["shared_node"] for item in shared}
    assert helios_network["helios"].id in shared_node_ids, (
        f"Helios not found in shared upstream. Found: {shared_node_ids}"
    )


def test_discover_hidden_dependencies_finds_helios(db, demo_company, helios_network, demo_membership):
    """
    Core test: discover_hidden_dependencies must detect that
    CirroTech, Northstar, ArcLight, SkyNode all share Helios upstream.
    """
    G = build_graph(db)
    findings = discover_hidden_dependencies(db, demo_company.id, G)

    assert len(findings) > 0, "Should find at least one hidden dependency"

    # Check that at least one finding references Helios
    helios_findings = [
        f for f in findings
        if f.shared_upstream_supplier_id == helios_network["helios"].id
    ]
    assert len(helios_findings) > 0, (
        f"No finding references Helios. Findings: {[(f.title, f.shared_upstream_supplier_id) for f in findings]}"
    )

    # That finding should be high or critical severity
    helios_finding = helios_findings[0]
    assert helios_finding.severity in ("high", "critical"), (
        f"Expected high/critical severity, got: {helios_finding.severity}"
    )

    # Confidence score should be meaningful
    assert helios_finding.confidence_score is not None
    assert helios_finding.confidence_score > 0.1


def test_discover_creates_db_records(db, demo_company, helios_network, demo_membership):
    """Findings should be persisted to DB."""
    from app.models.models import RiskFinding
    G = build_graph(db)
    findings = discover_hidden_dependencies(db, demo_company.id, G)

    db_findings = db.query(RiskFinding).filter(
        RiskFinding.company_id == demo_company.id,
        RiskFinding.finding_type == "hidden_dependency",
    ).all()
    assert len(db_findings) >= len(findings)


def test_discover_idempotent(db, demo_company, helios_network, demo_membership):
    """Running discovery twice should not duplicate findings."""
    from app.models.models import RiskFinding
    G = build_graph(db)
    findings1 = discover_hidden_dependencies(db, demo_company.id, G)
    count1 = db.query(RiskFinding).filter(RiskFinding.company_id == demo_company.id).count()

    findings2 = discover_hidden_dependencies(db, demo_company.id, G)
    count2 = db.query(RiskFinding).filter(RiskFinding.company_id == demo_company.id).count()

    assert count1 == count2, f"Duplicate findings created: {count1} vs {count2}"
