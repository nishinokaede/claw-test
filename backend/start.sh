#!/bin/bash
cd /root/jwt-auth-project/backend
source venv/bin/activate
python -m pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
