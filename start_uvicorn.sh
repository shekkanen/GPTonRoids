source .env
source venv/bin/activate
uvicorn prod.server:app --reload >> logs/uvicorn_prod.log 2>&1

