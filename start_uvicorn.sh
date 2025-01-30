source .env
source venv/bin/activate
uvicorn api.server:app --reload >> logs/uvicorn.log 2>&1

