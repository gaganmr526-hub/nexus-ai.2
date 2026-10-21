import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import ImportJob, User
from app.schemas.schemas import ImportJobRead
from app.deps import get_current_user, require_company_access
from app.services.import_service import (
    validate_suppliers_csv, commit_suppliers_import, get_template_csv
)
from datetime import datetime

router = APIRouter(prefix="/imports", tags=["imports"])


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    company_id: str = Query(...),
    import_type: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company_access(company_id, db, current_user)
    content = (await file.read()).decode("utf-8", errors="replace")

    if import_type == "suppliers":
        validation = validate_suppliers_csv(content, company_id)
    else:
        validation = {"total_rows": 0, "valid_rows": 0, "invalid_rows": 0, "errors": [], "preview": []}

    job = ImportJob(
        id=str(uuid.uuid4()),
        company_id=company_id,
        import_type=import_type,
        filename=file.filename,
        status="preview",
        total_rows=validation["total_rows"],
        valid_rows=validation["valid_rows"],
        invalid_rows=validation["invalid_rows"],
        error_count=len(validation["errors"]),
        result_json=json.dumps({"content": content, "validation": validation}),
        imported_by_id=current_user.id,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return {
        "job_id": job.id,
        "status": "preview",
        "total_rows": validation["total_rows"],
        "valid_rows": validation["valid_rows"],
        "invalid_rows": validation["invalid_rows"],
        "errors": validation["errors"][:20],
        "preview": validation.get("preview", []),
    }


@router.get("/{job_id}/preview")
def get_preview(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.query(ImportJob).filter(ImportJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Import job not found")
    require_company_access(job.company_id, db, current_user)
    result = {}
    if job.result_json:
        try:
            result = json.loads(job.result_json)
        except Exception:
            pass
    return {
        "job_id": job_id,
        "status": job.status,
        "total_rows": job.total_rows,
        "valid_rows": job.valid_rows,
        "preview": result.get("validation", {}).get("preview", []),
        "errors": result.get("validation", {}).get("errors", []),
    }


@router.post("/{job_id}/confirm")
def confirm_import(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.query(ImportJob).filter(ImportJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Import job not found")
    require_company_access(job.company_id, db, current_user)
    if job.status != "preview":
        raise HTTPException(status_code=400, detail=f"Job is in status '{job.status}', expected 'preview'")

    job.status = "importing"
    db.commit()

    try:
        result_data = json.loads(job.result_json or "{}")
        content = result_data.get("content", "")
        if job.import_type == "suppliers":
            imported = commit_suppliers_import(db, job, content, job.company_id)
        else:
            imported = 0
        job.status = "completed"
        job.result_json = json.dumps({**result_data, "imported_count": imported})
        job.updated_at = datetime.utcnow()
        db.commit()
        return {"job_id": job_id, "status": "completed", "imported_count": imported}
    except Exception as e:
        job.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=list[ImportJobRead])
def import_history(
    company_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company_access(company_id, db, current_user)
    return (
        db.query(ImportJob)
        .filter(ImportJob.company_id == company_id)
        .order_by(ImportJob.created_at.desc())
        .all()
    )


@router.get("/templates/{import_type}")
def download_template(import_type: str, current_user: User = Depends(get_current_user)):
    from fastapi.responses import PlainTextResponse
    content = get_template_csv(import_type)
    return PlainTextResponse(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={import_type}_template.csv"},
    )
