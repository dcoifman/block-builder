# app/index.py
from app import app as application

# Optional: Add any Vercel-specific startup code here if needed in the future.
# For now, just making the Flask app instance available is usually enough.

# The variable 'application' (or 'app') is typically what WSGI servers like Gunicorn,
# and by extension Vercel's Python runtime, look for.
# We are aliasing our Flask app instance ('app' from app/__init__.py) to 'application'
# as 'application' is a common convention for WSGI entry points.
# If Vercel's Python runtime specifically looks for 'app', this can be:
# from app import app
# However, 'application' is a safer bet for WSGI compatibility.
# Let's stick to aliasing to 'application' for now.
