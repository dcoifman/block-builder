# Deploying the Strength Tracker Flask App to Vercel

## 1. Introduction

This guide provides step-by-step instructions for deploying the Strength Tracker Flask application to Vercel. Vercel is a platform primarily known for frontend frameworks and static sites, but it also supports serverless functions, which allow us to run Python/Flask applications like this one.

## 2. Prerequisites

*   **Vercel Account:** You'll need an account with Vercel. You can sign up for free at [vercel.com/signup](https://vercel.com/signup).
*   **Git:** Ensure Git is installed on your local machine.
*   **Project Code on Git Provider:** Your project's code should be pushed to a Git repository (e.g., GitHub, GitLab, Bitbucket) as Vercel deploys by connecting to these providers.

## 3. Project Configuration for Vercel

Your project has been pre-configured with the following files to facilitate Vercel deployment:

*   **`vercel.json`:** This file in the project root tells Vercel how to build and route your application. It defines the Python runtime, build commands, static file handling, and environment variables.
    *   Key aspects of `vercel.json` include:
        *   `builds`: Specifies how to build the Python application, pointing to `app/index.py` and using the `@vercel/python` builder. It also includes the `buildCommand: "bash build_vercel.sh"` to run our custom build script.
        *   `routes`: Manages how incoming requests are directed.
            *   `{ "src": "/static/(.*)", "dest": "/app/static/$1" }`: This rule explicitly maps URL paths starting with `/static/` (e.g., `/static/css/style.css`) to the `app/static/` directory within your project structure. This helps Vercel's edge network efficiently serve static assets like CSS and JavaScript files.
            *   `{ "src": "/(.*)", "dest": "app/index.py" }`: This is a fallback rule that forwards all other requests to your Flask application (via `app/index.py`).
        *   `env`: Sets server-side environment variables like `FLASK_APP`, `FLASK_ENV`, and `PYTHONPATH`.
*   **`app/index.py`:** This is the primary entry point for the application when deployed on Vercel. It makes the Flask app instance available to Vercel's Python runtime. Crucially, this file must make the Flask application instance available as a global variable named specifically `app` or `handler`. For example: `from app import app` (if your Flask instance in `app/__init__.py` is named `app`). Vercel's Python runtime looks for one of these specific variable names to serve the application.
*   **`build_vercel.sh`:** A shell script located in the project root. It's configured in `vercel.json` as a custom build command. This script installs Python dependencies and attempts to initialize and seed the SQLite database (`app.db`) during Vercel's build process.
*   **`requirements.txt`:** This file lists all the Python dependencies (like Flask, SQLAlchemy, Gunicorn) required by the application.

## 4. Deployment Steps

**Step 1: Import Project on Vercel**

1.  Log in to your Vercel account.
2.  From your dashboard, click "Add New..." and select "Project".
3.  Connect Vercel to your Git provider (e.g., GitHub) if you haven't already.
4.  Choose the repository for your Strength Tracker application from the list.

**Step 2: Configure Project Settings**

Vercel is usually good at auto-detecting settings, especially with a `vercel.json` file present.

*   **Framework Preset:** Vercel should automatically detect that this is a Python project due to the `vercel.json` configuration using `@vercel/python`. If you need to choose, select "Other".
*   **Build and Output Settings:**
    *   These settings should be automatically configured based on your `vercel.json` file.
    *   **Build Command:** Verify this is set to `bash build_vercel.sh`. If not, you can override it in the Vercel UI in "Build & Development Settings".
    *   **Output Directory:** This is typically not applicable for Python serverless functions in the same way it is for static site generators. Vercel handles the output packaging.
    *   **Install Command:** This should be handled by `bash build_vercel.sh` (which runs `pip install -r requirements.txt`). If Vercel has a separate "Install Command" field, it might also show `pip install -r requirements.txt` or you can ensure it's set there.
*   **Root Directory:** Ensure this is set to the root of your project (where `vercel.json` is located). If your project is in a monorepo subdirectory, adjust accordingly.

**Step 3: Environment Variables**

Before deploying, you need to set a crucial environment variable.

1.  In your Vercel project dashboard, navigate to "Settings" -> "Environment Variables".
2.  Add the following variable:
    *   **`SECRET_KEY`**:
        *   **Key:** `SECRET_KEY`
        *   **Value:** Generate a strong, random string. You can use your local Python to generate one:
            ```bash
            python -c "import secrets; print(secrets.token_hex(24))"
            ```
            Copy the output and paste it as the value.
        *   **Scope:** Ensure it's available for all environments (Production, Preview, Development).
    *   **`DATABASE_URL`**:
        *   **DO NOT set a `DATABASE_URL` environment variable** if you intend to use the SQLite database (`app.db`) that is created and seeded during the build process (via `build_vercel.sh`). The application's `config.py` is designed to fall back to the local `app.db` if `DATABASE_URL` is not set.
    *   **Other Variables:**
        *   `FLASK_APP` and `FLASK_ENV` are already set in `vercel.json`. They generally do not need to be set again here unless you need to override them for specific Vercel environments.

**Step 4: Deploy**

1.  After configuring the project and environment variables, go back to your project's overview page on Vercel.
2.  Click the "Deploy" button (this might be automatic if you've just imported the project, or you might need to trigger a deployment from the "Deployments" tab).
3.  Vercel will start the build process. You can monitor the build logs in real-time from the Vercel dashboard. This is where you'll see the output of `build_vercel.sh`, including the database initialization steps.

## 5. Post-Deployment

*   **Accessing the App:** Once the deployment is successful, Vercel will provide you with one or more URLs (e.g., `your-project-name.vercel.app`). You can use these to access your live application.
*   **Viewing Logs:**
    *   **Build Logs:** Available during and after the deployment in the "Deployments" section of your Vercel project.
    *   **Runtime Logs (Function Logs):** To see logs from your running Flask application (e.g., request logs, errors from your Python code), go to your Vercel project dashboard, select the relevant deployment, and navigate to the "Functions" tab. Click on the function corresponding to `app/index.py` to view its logs.

## 6. Database Considerations: SQLite on Vercel

This project uses SQLite as its database. When deploying to Vercel, there are important considerations:

**1. Build-Time Database Initialization:**
*   The `vercel.json` configuration includes a `buildCommand` that executes `build_vercel.sh`.
*   This script (`build_vercel.sh`) performs the following steps during Vercel's build process:
    1.  Installs Python dependencies from `requirements.txt`.
    2.  Sets necessary environment variables (`PYTHONPATH`, `FLASK_APP`).
    3.  Runs the Flask CLI commands: `flask init-db`, `flask populate-exercises`, and `flask populate-ratios`.
*   This process creates the `app.db` SQLite file and populates it with initial data. This `app.db` file is then included in the deployment package.
*   As a result, the application should deploy with a pre-seeded database.

**2. Ephemeral Filesystem for Live Data:**
*   Vercel's serverless functions have an ephemeral (temporary) filesystem.
*   **Any new data written to the SQLite database by the live application (e.g., new user registrations, new workout logs after deployment) will be lost when the serverless function instance recycles, a new deployment occurs, or the instance scales down.**
*   The data seeded during the build process will be present each time a new instance starts from a fresh deployment.

**3. `DATABASE_URL` Configuration:**
*   The application's `config.py` is set up to use the `DATABASE_URL` environment variable if provided.
*   For this Vercel deployment with SQLite, **do not set a `DATABASE_URL` environment variable on Vercel**.
*   When `DATABASE_URL` is not set, the configuration defaults to `sqlite:///app.db`, which will use the `app.db` file created in the project root during the build process.

**4. Potential Issues & Fallbacks for `build_vercel.sh`:**
*   **Permissions:** If there are issues with file system permissions in the Vercel build environment, creating `app.db` might fail. Check build logs carefully.
*   **`flask` command:** The script attempts to use `python -m flask` if `flask` is not directly on the PATH, which should be robust.
*   **Fallback - Local Seeding (Use with Caution):** If the build script consistently fails to create/seed `app.db` on Vercel:
    1.  Run the database initialization commands locally:
        ```bash
        # Ensure your local FLASK_APP is set (e.g., export FLASK_APP=run.py or app:app)
        flask init-db
        flask populate-exercises
        flask populate-ratios
        ```
    2.  This will create/update `app.db` in your local project root.
    3.  Commit this `app.db` file to your Git repository *specifically for the Vercel deployment*.
    4.  Remove or modify `build_vercel.sh` to not run these commands if you are committing a pre-built `app.db`.
    5.  Deploy to Vercel. Vercel will then deploy your committed `app.db`.
    *   **Caution:** This approach is generally not ideal for databases in version control but can be a temporary workaround for MVPs on platforms with ephemeral filesystems when build-time seeding is problematic. Remember that any data written by the live app will still be lost.

**5. Long-Term Solution:**
*   For persistent data storage and a more robust production setup, it is **highly recommended** to use a managed cloud database service (e.g., Vercel Postgres, Neon, Supabase, ElephantSQL, or AWS RDS).
*   This would involve:
    1.  Setting up the cloud database instance.
    2.  Setting the `DATABASE_URL` environment variable on Vercel to point to your cloud database (e.g., `postgresql://user:password@host:port/database`).
    3.  Adding the appropriate database driver (like `psycopg2-binary` for PostgreSQL) to `requirements.txt`.
    4.  Removing the SQLite-specific seeding from `build_vercel.sh` (database schema migrations would be handled differently, often with tools like Flask-Migrate, run against the live cloud database).

## 7. Troubleshooting Tips

*   **Build Failures:** Carefully examine the build logs on Vercel. They usually provide good insights into what went wrong (e.g., dependency installation issues, errors in `build_vercel.sh`).
*   **Import Errors:** If your application has trouble finding modules, ensure `PYTHONPATH` is set correctly (as done in `vercel.json` and `build_vercel.sh`) and that your `app/index.py` can access the Flask app instance.
*   **Environment Variable Issues:** Double-check that your `SECRET_KEY` is set correctly in the Vercel project settings and that you haven't unintentionally set `DATABASE_URL` when using the build-time SQLite.
*   **Function Logs:** For runtime errors (after deployment), check the Function Logs in the Vercel dashboard.
*   **Vercel Documentation:** Vercel's official documentation for Python deployments is a valuable resource: [vercel.com/docs/frameworks/python](https://vercel.com/docs/frameworks/python)

By following these steps, you should be able to successfully deploy and run your Strength Tracker Flask application on Vercel. Remember the limitations of SQLite for live data on this platform.I have created the `deployment_guide_vercel.md` file in the project root and populated it with the detailed sections and information as requested.

The guide covers:
*   Introduction to deploying on Vercel.
*   Prerequisites (Vercel account, Git, code on a Git provider).
*   An overview of the project's Vercel-specific configuration files (`vercel.json`, `app/index.py`, `build_vercel.sh`).
*   Step-by-step deployment instructions, including importing the project, configuring settings, setting environment variables (with a crucial note about `DATABASE_URL` for SQLite), and monitoring the deployment.
*   Post-deployment information on accessing the app and viewing logs.
*   A comprehensive "Database Considerations" section, incorporating the previously prepared documentation on SQLite's behavior on Vercel, the build-time initialization process, the ephemeral nature of live data, and the recommendation for a managed cloud database for production use.
*   Basic troubleshooting tips and a link to Vercel's official Python documentation.

The tone is instructional, and the content is structured to guide a user through the deployment process, highlighting important considerations, especially regarding the database.
