from fastapi import APIRouter
from app.api.v1 import (
    auth, companies, suppliers, relationships, graph,
    dependencies, risks, scenarios, impact, alternatives,
    recovery, procurement, imports, reports, notifications,
    audit, health
)

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(companies.router)
router.include_router(suppliers.router)
router.include_router(relationships.router)
router.include_router(graph.router)
router.include_router(dependencies.router)
router.include_router(risks.router)
router.include_router(scenarios.router)
router.include_router(impact.router)
router.include_router(alternatives.router)
router.include_router(recovery.router)
router.include_router(procurement.router)
router.include_router(imports.router)
router.include_router(reports.router)
router.include_router(notifications.router)
router.include_router(audit.router)
router.include_router(health.router)
