"""Vercel Serverless Function Entry Point.

Vercel erwartet eine FastAPI-App unter api/index.py.
Wir importieren einfach die bestehende App.
"""
from app.main import app
