# Heroku Deployment Guide for Strength Tracker App

This guide outlines the steps to deploy the Strength Tracker Flask application to Heroku.

## Prerequisites

1.  **Heroku Account:** Sign up for a free account at [heroku.com](https://www.heroku.com/).
2.  **Heroku CLI:** Install the Heroku Command Line Interface. You can download it from [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli).
3.  **Git:** Ensure Git is installed on your local machine.
4.  **Python Environment:** A local Python environment (matching `runtime.txt`, e.g., Python 3.10.12) with all dependencies from `requirements.txt` installed.

## Deployment Steps

**1. Login to Heroku CLI:**
   Open your terminal or command prompt and run:
   ```bash
   heroku login
   ```
   This will open a browser window for you to log in.

**2. Navigate to Your Project Directory:**
   Open your terminal and change the directory to the root of your Strength Tracker application (where `run.py`, `Procfile`, etc., are located).
   ```bash
   cd path/to/your/strength-tracker-app
   ```

**3. Initialize Git Repository (if not already done):**
   If your project is not already a Git repository, initialize it:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for Heroku deployment"
   ```
   *Note: Ensure `.venv` (or your virtual environment folder), `__pycache__/`, `instance/app.db` (if you switch to instance folder for local dev), and other unnecessary files are in your `.gitignore` file.*

**4. Create a New Heroku App:**
   Create a new application on Heroku. You can either let Heroku generate a name or specify your own (must be unique).
   ```bash
   heroku create your-unique-app-name
   ```
   (Replace `your-unique-app-name` with your desired app name. If you omit it, Heroku will generate one.)
   This command also adds a Heroku remote (usually named `heroku`) to your Git configuration.

**5. Set Environment Variables on Heroku:**

   *   **`SECRET_KEY`:**
      Your application's `SECRET_KEY` should be a strong, random string and must be set in the Heroku environment. You can generate one locally and set it:
      ```bash
      # Generate a secret key (run this in your local Python console or a script)
      # python -c 'import secrets; print(secrets.token_hex(24))' 
      # Copy the output, then set it on Heroku:
      heroku config:set SECRET_KEY="your_generated_secret_key_here" 
      ```
      Alternatively, you can have Heroku generate one and set it in one command (less secure if your shell history is compromised):
      ```bash
      heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(24))')
      ```

   *   **`DATABASE_URL` (for SQLite - Default for this MVP):**
      The application is currently configured to use SQLite. On Heroku, SQLite is ephemeral (data resets on dyno restarts). For this MVP, we'll proceed with SQLite. Heroku doesn't automatically provide a `DATABASE_URL` for SQLite. The app will create an `app.db` file on the dyno's filesystem. No `DATABASE_URL` needs to be set for this default SQLite behavior.

   *   **`DATABASE_URL` (Optional - If switching to Heroku Postgres for persistence):**
      If you need persistent data, you should use Heroku Postgres (a free tier is available).
      1.  Provision the addon:
          ```bash
          heroku addons:create heroku-postgresql:hobby-dev
          ```
      2.  Heroku will automatically set a `DATABASE_URL` environment variable for your app, which the `config.py` is set up to use.
      3.  You would also need to install `psycopg2-binary` (add it to `requirements.txt` before pushing):
          ```bash
          pip install psycopg2-binary
          pip freeze > requirements.txt 
          # (Then commit the change to requirements.txt)
          ```

**6. Push Code to Heroku:**
   Deploy your code to Heroku using Git. This will push your `main` branch (or `master` if that's your default) to the `heroku` remote.
   ```bash
   git push heroku main 
   ```
   (Or `git push heroku master` if your main branch is named `master`).
   Heroku will detect it's a Python app, install dependencies from `requirements.txt`, and use the command in `Procfile` to start your web server.

**7. Run Database Initialization and Seeding Commands:**
   Once the app is deployed, you need to initialize the database schema and populate it with initial data using the Flask CLI commands.
   ```bash
   heroku run flask init-db
   heroku run flask populate-exercises
   heroku run flask populate-ratios
   ```
   *Note: `heroku run` executes commands in a one-off dyno.*

**8. Open the App:**
   After the commands complete successfully, open your application in the browser:
   ```bash
   heroku open
   ```

**9. View Logs (Troubleshooting):**
   If you encounter any issues or your app doesn't start correctly, you can view the logs:
   ```bash
   heroku logs --tail
   ```
   This will show real-time logs. For more specific logs, you can use `heroku logs`.

## Post-Deployment Notes

*   **SQLite Ephemeral Nature:** Remember that if you are using SQLite, the database will be reset if your dyno restarts (which Heroku does periodically, e.g., daily, or when you deploy new code or change config vars). For persistent storage, use Heroku Postgres as outlined in Step 5.
*   **Scaling:** The free dyno tier has limitations. If your app grows, you might need to scale to paid dyno types.
*   **Custom Domain:** You can configure a custom domain for your Heroku app through the Heroku dashboard.
*   **Further Configuration:** Additional settings (like `FLASK_ENV=production`) can be set via `heroku config:set`. However, Gunicorn typically handles the production environment settings for Flask.

You should now have a running instance of the Strength Tracker application on Heroku!
