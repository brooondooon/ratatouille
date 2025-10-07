"""
Vercel serverless function wrapper for FastAPI backend
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app import app

# Vercel expects a handler
handler = app
