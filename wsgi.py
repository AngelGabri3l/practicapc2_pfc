"""Punto de entrada para gunicorn."""
from app import create_app

app = create_app()
