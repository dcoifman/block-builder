# app/index.py
from app import app

# Vercel's Python runtime looks for a variable named 'app' or 'handler'.
# By ensuring the Flask instance imported from app/__init__.py is named 'app'
# in this file, we comply with Vercel's requirement.
