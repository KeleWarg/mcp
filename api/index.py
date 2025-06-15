# api/index.py  – Vercel looks for an ASGI callable named `app`.
import sys
import os
from pathlib import Path

# Add the parent directory to Python path so we can import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app   # re-export the FastAPI instance