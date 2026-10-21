cd nexustrace-ai\backend
pip install -r requirements.txt
python scripts\generate_demo_data.py
python -c "from app.database import engine, Base; import app.models.models; Base.metadata.create_all(bind=engine); print('Tables created')"
python scripts\seed_db.py
uvicorn app.main:app --reload --port 8000
