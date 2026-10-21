import json
from collections import defaultdict, deque
from datetime import datetime
from typing import Optional
import networkx as nx
from sqlalchemy.orm import Session
from app.models.models import (
    Scenario, ScenarioResult, Supplier, Component, BillOfMaterial,
    Product, InventorySnapshot, DemandForecast, MitigationOption
)
from app.graph.builder import build_graph
import uuid


def calculate_inventory_coverage(
    quantity_on_hand: float,
    daily_demand: float,
    disruption_days: int,
) -> dict:
    if daily_demand <= 0:
        return {"days_coverage": 999, "shortfall_units": 0.0, "coverage_ratio": 1.0}
    days_coverage = quantity_on_hand / daily_demand
    total_demand = daily_demand * disruption_days
    shortfall = max(0.0, total_demand - quantity_on_hand)
    coverage_ratio = min(1.0, quantity_on_hand / total_demand) if total_demand > 0 else 1.0
    return {
        "days_coverage": round(days_coverage, 2),
        "shortfall_units": round(shortfall, 2),
        "coverage_ratio": round(coverage_ratio, 4),
    }


def estimate_revenue_exposure(
    affected_product_ids: set[str],
    disruption_days: int,
    db: Session,
    shortfall_fractions: dict[str, float],
) -> dict:
    """Calculate revenue exposure without double-counting."""
    total_revenue = 0.0
    breakdown = {}
    for pid in affected_product_ids:
        product = db.query(Product).filter(Product.id == pid).first()
        if product and product.daily_demand and product.revenue_per_unit:
            fraction = shortfall_fractions.get(pid, 1.0)
            exposure = product.daily_demand * product.revenue_per_unit * disruption_days * fraction
            total_revenue += exposure
            breakdown[pid] = {
                "product_name": product.name,
                "daily_demand": product.daily_demand,
                "revenue_per_unit": product.revenue_per_unit,
                "exposure": round(exposure, 2),
                "shortfall_fraction": round(fraction, 4),
            }
    return {"total_revenue_exposure": round(total_revenue, 2), "breakdown": breakdown}


def calculate_financial_impact(
    shortfalls: dict[str, float],
    products: list,
) -> dict:
    total_cost = sum(shortfalls.values())
    return {
        "total_estimated_cost": round(total_cost, 2),
        "shortfalls": {k: round(v, 2) for k, v in shortfalls.items()},
    }


def run_scenario(db: Session, scenario: Scenario, G: Optional[nx.DiGraph] = None) -> ScenarioResult:
    """
    Graph traversal disruption propagation:
    1. Mark target supplier as disrupted (capacity_reduction_pct).
    2. BFS downstream through depends_on edges.
    3. For each affected node, check inventory coverage.
    4. Roll up to products, companies.
    5. Calculate financials (no double-counting).
    """
    if G is None:
        G = build_graph(db)

    target_id = scenario.target_supplier_id
    capacity_reduction = (scenario.capacity_reduction_pct or 100.0) / 100.0
    duration_days = scenario.duration_days or 30

    # BFS propagation
    directly_affected = set()
    indirectly_affected = set()

    if target_id and target_id in G:
        directly_affected.add(target_id)
        # BFS downstream (descendants depend on target)
        visited = set()
        queue = deque([target_id])
        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            # Nodes that directly depend on this node (incoming edges from dependents)
            # In our graph: A -> B means "A depends_on B" or "A supplies B"
            # Downstream impact: who depends on target? Predecessors in depends_on edges
            for pred in G.predecessors(node):
                edge_data = G.edges[pred, node]
                rel_type = edge_data.get("relationship_type", "")
                if rel_type in ("depends_on", "supplies", "manufactures", "produces_from"):
                    if pred != target_id:
                        indirectly_affected.add(pred)
                    queue.append(pred)

    all_affected = directly_affected | indirectly_affected
    affected_supplier_ids = list(all_affected)

    # Find affected components
    affected_components = set()
    if affected_supplier_ids:
        comps = (
            db.query(Component)
            .filter(Component.supplier_id.in_(affected_supplier_ids))
            .all()
        )
        for c in comps:
            affected_components.add(c.id)

    # Find affected products via BOM
    affected_products = set()
    shortfall_fractions: dict[str, float] = {}

    for comp_id in affected_components:
        bom_entries = (
            db.query(BillOfMaterial)
            .filter(BillOfMaterial.component_id == comp_id)
            .all()
        )
        for bom in bom_entries:
            affected_products.add(bom.product_id)

    # Calculate inventory coverage per component
    component_shortfalls: dict[str, float] = {}
    component_coverages: dict[str, dict] = {}

    for comp_id in affected_components:
        # Get inventory
        inv = (
            db.query(InventorySnapshot)
            .filter(
                InventorySnapshot.component_id == comp_id,
                InventorySnapshot.company_id == scenario.company_id,
            )
            .order_by(InventorySnapshot.snapshot_date.desc())
            .first()
        )
        qty = inv.quantity_on_hand if inv else 0.0

        # Get demand (from products using this component)
        total_daily_demand = 0.0
        bom_entries = (
            db.query(BillOfMaterial)
            .filter(BillOfMaterial.component_id == comp_id)
            .all()
        )
        for bom in bom_entries:
            product = db.query(Product).filter(Product.id == bom.product_id).first()
            if product and product.daily_demand:
                total_daily_demand += product.daily_demand * bom.quantity_required

        # Apply capacity reduction and substitute availability
        effective_supply_reduction = capacity_reduction
        if scenario.substitute_availability == "partial":
            effective_supply_reduction *= 0.5
        elif scenario.substitute_availability == "full":
            effective_supply_reduction = 0.0

        effective_daily_demand = total_daily_demand * effective_supply_reduction
        coverage = calculate_inventory_coverage(qty, effective_daily_demand, duration_days)
        component_coverages[comp_id] = coverage
        component_shortfalls[comp_id] = coverage["shortfall_units"]

    # Roll up shortfalls to products (avoid double-counting by tracking affected product set)
    product_shortfall_fractions: dict[str, float] = {}
    for prod_id in affected_products:
        bom_entries = (
            db.query(BillOfMaterial)
            .filter(BillOfMaterial.product_id == prod_id)
            .all()
        )
        product = db.query(Product).filter(Product.id == prod_id).first()
        if not product:
            continue

        max_fraction = 0.0
        for bom in bom_entries:
            if bom.component_id in affected_components:
                cov = component_coverages.get(bom.component_id, {})
                fraction = 1.0 - cov.get("coverage_ratio", 0.0)
                max_fraction = max(max_fraction, fraction)

        product_shortfall_fractions[prod_id] = max_fraction

    # Financial calculations
    revenue_data = estimate_revenue_exposure(
        affected_products, duration_days, db, product_shortfall_fractions
    )

    total_shortfall_units = sum(component_shortfalls.values())
    financial = calculate_financial_impact(component_shortfalls, [])

    # Residual risk score
    recovery_days = scenario.recovery_lead_time_days or 60
    if not affected_supplier_ids:
        residual_risk = 0.0
    else:
        residual_risk = min(1.0, len(affected_supplier_ids) / max(len(G.nodes), 1) * 0.5
                           + capacity_reduction * 0.3
                           + (duration_days / 365) * 0.2)

    assumptions = {
        "duration_days": duration_days,
        "capacity_reduction_pct": scenario.capacity_reduction_pct,
        "inventory_assumption": scenario.inventory_assumption,
        "demand_level": scenario.demand_level,
        "substitute_availability": scenario.substitute_availability,
        "recovery_lead_time_days": recovery_days,
    }

    result_detail = {
        "affected_supplier_ids": affected_supplier_ids,
        "affected_component_ids": list(affected_components),
        "affected_product_ids": list(affected_products),
        "component_shortfalls": {k: round(v, 2) for k, v in component_shortfalls.items()},
        "revenue_breakdown": revenue_data.get("breakdown", {}),
    }

    # Check if result already exists
    existing = (
        db.query(ScenarioResult)
        .filter(ScenarioResult.scenario_id == scenario.id)
        .first()
    )

    if existing:
        # Update
        existing.direct_affected_count = len(directly_affected)
        existing.indirect_affected_count = len(indirectly_affected)
        existing.affected_components_count = len(affected_components)
        existing.affected_products_count = len(affected_products)
        existing.exposed_companies_count = 1
        existing.estimated_revenue_exposure = revenue_data["total_revenue_exposure"]
        existing.estimated_cost = financial["total_estimated_cost"]
        existing.estimated_shortfall_units = round(total_shortfall_units, 2)
        existing.recovery_duration_days = recovery_days
        existing.residual_risk_score = round(residual_risk, 4)
        existing.assumptions_json = json.dumps(assumptions)
        existing.result_json = json.dumps(result_detail)
        existing.calculated_at = datetime.utcnow()
        db.flush()
        result = existing
    else:
        result = ScenarioResult(
            id=str(uuid.uuid4()),
            scenario_id=scenario.id,
            direct_affected_count=len(directly_affected),
            indirect_affected_count=len(indirectly_affected),
            affected_components_count=len(affected_components),
            affected_products_count=len(affected_products),
            exposed_companies_count=1,
            estimated_revenue_exposure=revenue_data["total_revenue_exposure"],
            estimated_cost=financial["total_estimated_cost"],
            estimated_shortfall_units=round(total_shortfall_units, 2),
            recovery_duration_days=recovery_days,
            residual_risk_score=round(residual_risk, 4),
            currency="USD",
            assumptions_json=json.dumps(assumptions),
            result_json=json.dumps(result_detail),
        )
        db.add(result)
        db.flush()

    # Generate mitigation options
    _generate_mitigation_options(db, scenario, result, affected_products, affected_components)

    db.commit()
    return result


def _generate_mitigation_options(
    db: Session,
    scenario: Scenario,
    result: ScenarioResult,
    affected_products: set,
    affected_components: set,
) -> None:
    # Clear existing
    db.query(MitigationOption).filter(MitigationOption.scenario_id == scenario.id).delete()

    revenue_exposure = result.estimated_revenue_exposure

    options = [
        {
            "option_type": "dual_sourcing",
            "description": "Qualify and onboard an alternative supplier for affected components within 30-60 days.",
            "estimated_cost": revenue_exposure * 0.05,
            "time_to_implement_days": 45,
            "expected_shortage_reduction_pct": 60.0,
            "expected_revenue_protection": revenue_exposure * 0.6,
            "residual_risk_score": 0.3,
            "ranking_score": 0.85,
        },
        {
            "option_type": "safety_stock",
            "description": "Increase safety stock for all critical components by 60 days of supply.",
            "estimated_cost": revenue_exposure * 0.08,
            "time_to_implement_days": 15,
            "expected_shortage_reduction_pct": 40.0,
            "expected_revenue_protection": revenue_exposure * 0.4,
            "residual_risk_score": 0.5,
            "ranking_score": 0.65,
        },
        {
            "option_type": "demand_reduction",
            "description": "Reduce production volume by 30% to extend existing inventory coverage.",
            "estimated_cost": revenue_exposure * 0.30,
            "time_to_implement_days": 5,
            "expected_shortage_reduction_pct": 30.0,
            "expected_revenue_protection": revenue_exposure * 0.1,
            "residual_risk_score": 0.6,
            "ranking_score": 0.45,
        },
    ]

    for opt in options:
        db.add(MitigationOption(
            id=str(uuid.uuid4()),
            scenario_id=scenario.id,
            currency="USD",
            **opt,
        ))
