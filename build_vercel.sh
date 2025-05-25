#!/bin/bash
echo "Starting Vercel build process..."

# Install dependencies
# Vercel's @vercel/python builder typically handles this automatically based on requirements.txt.
# Explicitly running it here ensures it happens before our custom scripts,
# though it might be redundant depending on Vercel's exact build sequence.
# Adding --user to avoid permission issues if Vercel runs this as a non-root user in some contexts.
pip install --user -r requirements.txt

echo "Dependencies installed."

# Set PYTHONPATH to ensure Flask app can be found by the flask command
export PYTHONPATH=$(pwd):$PYTHONPATH
# Ensure Flask CLI can find the app (app:app should work if app/index.py or app/__init__.py defines 'app')
# The FLASK_APP env var is also set in vercel.json, but being explicit here can help.
export FLASK_APP=app:app 

echo "Running database setup..."
# Ensure the Flask command is callable. If pip install --user puts scripts in ~/.local/bin,
# that path needs to be in PATH. Vercel's environment should handle this for installed packages.
# If 'flask' command is not found, try 'python -m flask'
if command -v flask &> /dev/null
then
    FLASK_COMMAND="flask"
else
    echo "'flask' command not found, attempting 'python -m flask'"
    FLASK_COMMAND="python -m flask"
fi

$FLASK_COMMAND init-db
$FLASK_COMMAND populate-exercises
$FLASK_COMMAND populate-ratios

echo "Database setup complete. SQLite database should be created/populated."
echo "Vercel build process finished."
