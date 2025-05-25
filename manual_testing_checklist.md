# Manual Testing Checklist - Strength Tracker App

## I. Onboarding & Setup

**1. Registration:**
    *   **Step 1.1:** Navigate to the base URL (`/`).
        *   *Expected:* Redirected to the Login page (`/auth/login`).
    *   **Step 1.2:** Click the "Register here" link.
        *   *Expected:* Navigated to the Registration page (`/auth/register`), registration form is displayed with fields: Username, Email, Password, Confirm Password.
    *   **Step 1.3:** Attempt to register with mismatched passwords (e.g., 'password123' and 'password321').
        *   *Expected:* Registration fails. A flash message "Passwords do not match." is displayed on the registration page.
    *   **Step 1.4:** Attempt to register with an email or username that already exists (if a user was pre-registered or created in a previous test).
        *   *Expected:* Registration fails. A flash message "Username or email already exists." is displayed.
    *   **Step 1.5:** Attempt to register with missing fields (e.g., empty username).
        *   *Expected:* Registration fails. A flash message "All fields are required." (or browser validation prevents submission).
    *   **Step 1.6:** Register with valid, unique details.
        *   *Expected:* Registration succeeds. Redirected to the Login page. A flash message "Registration successful! Please login." is displayed.

**2. Login & Logout:**
    *   **Step 2.1:** Navigate to the Login page (`/auth/login`).
        *   *Expected:* Login form is displayed with fields: Email, Password.
    *   **Step 2.2:** Attempt to login with incorrect credentials (e.g., valid email, wrong password).
        *   *Expected:* Login fails. A flash message "Invalid email or password." is displayed on the login page.
    *   **Step 2.3:** Login with the correct credentials of the user created in Step 1.6.
        *   *Expected:* Login succeeds. Redirected to the Dashboard page (`/dashboard`). A flash message "Login successful!" is displayed. User's username is visible in the navigation.
    *   **Step 2.4:** From the Dashboard, click the "Logout" link in the navigation.
        *   *Expected:* Logout succeeds. Redirected to the Login page. A flash message "You have been logged out." is displayed.

**3. Initial 1RM Entry (on Dashboard):**
    *   **Step 3.1:** Login as a test user. Navigate to the Dashboard.
        *   *Expected:* Dashboard page is displayed. "Your One-Rep Maxes (1RMs)" section shows "Loading your maxes..." or "No maxes recorded yet."
    *   **Step 3.2:** Verify the "Exercise" dropdown in the "Add/Update 1RM" form is populated with exercises (e.g., Back Squat, Bench Press).
        *   *Expected:* Dropdown contains a list of exercises.
    *   **Step 3.3:** Select "Back Squat" from the dropdown, enter a valid weight (e.g., 100) and click "Save Max".
        *   *Expected:* A success message "User max added successfully" (or similar) is displayed. The "Your One-Rep Maxes (1RMs)" list updates to show "Back Squat: 100 kg".
    *   **Step 3.4:** Select "Bench Press", enter a valid weight (e.g., 70) and click "Save Max".
        *   *Expected:* Success message. List updates with "Bench Press: 70 kg".
    *   **Step 3.5:** Select "Back Squat" again, enter a new weight (e.g., 105) and click "Save Max".
        *   *Expected:* Success message "User max updated successfully". List updates to show "Back Squat: 105 kg".

## II. Viewing Poliquin Ratio Targets (on Dashboard)

    *   **Step 4.1:** With 1RMs entered for "Back Squat" (105kg) and "Bench Press" (70kg), view the "Poliquin Ratio Targets" section on the Dashboard.
        *   *Expected:* Targets are displayed. For example:
            *   "Front Squat (Target): 89.25 kg (Based on Back Squat 1RM of 105kg at 85%)" (105 * 0.85 = 89.25)
            *   "Close Grip Bench Press (Target): 63 kg (Based on Bench Press 1RM of 70kg at 90%)" (70 * 0.90 = 63)
            *   Other relevant targets based on default ratios.
    *   **Step 4.2:** If a primary exercise for a ratio has no 1RM set (e.g., Deadlift for Romanian Deadlift ratio, if Deadlift 1RM is not set), that specific target should not appear or should indicate missing data.
        *   *Expected:* List is shorter or relevant entries show a message indicating missing primary 1RM.

## III. Generating & Viewing a Program

    *   **Step 5.1:** Login and navigate to the "Program" page from the navigation.
        *   *Expected:* The "Your Training Program" page is displayed. Initially shows "Loading your program...".
    *   **Step 5.2:** Wait for the program to load.
        *   *Expected:* A 4-week program is displayed, structured by Week and Day. Each exercise entry shows: Exercise Name, Type, Sets, Reps, Target Weight, Intensity %, Notes, and a "Log This" button.
            *   Target weights for "main" lifts should be calculated based on entered 1RMs (e.g., Back Squat Week 1 @75% of 105kg = 78.75kg, rounded to 77.5kg).
            *   Target weights for main lifts without a 1RM should show "1RM not set".
            *   Accessory lifts should show "As prescribed / RPE based".
    *   **Step 5.3:** If no relevant 1RMs are set for any main exercises in the program template.
        *   *Expected:* Program still loads, but all main exercises show "1RM not set" for target weight.

## IV. Logging a Workout

**1. Logging from Program Page:**
    *   **Step 6.1.1:** On the "Program" page, find an exercise (e.g., Week 1, Day 1 - Back Squat). Click its "Log This" button.
        *   *Expected:* The "Log a Workout" form at the bottom of the page is pre-filled with:
            *   Exercise Name: Back Squat
            *   Sets: (e.g., 3)
            *   Reps: (e.g., 8)
            *   Weight: (e.g., 77.5 kg - the calculated target weight for that day)
            *   Date Logged: Today's date.
    *   **Step 6.1.2:** Adjust reps if necessary (e.g., actual reps performed: 7). Click "Log Workout".
        *   *Expected:* Success message "Workout logged successfully!" is displayed. The form fields are cleared (or reset to defaults like today's date).
    *   **Step 6.1.3:** Attempt to log with a missing field (e.g., clear the 'sets' field). Click "Log Workout".
        *   *Expected:* Error message "All fields are required." (or similar) is displayed. Log is not saved.
    *   **Step 6.1.4:** Fill the form manually (without "Log This") with a new exercise not from the program (e.g., "Pull-up", 3 sets, 8 reps, 0 weight (bodyweight), today's date). Click "Log Workout".
        *   *Expected:* Success message. Log is saved.

## V. Viewing Workout History

    *   **Step 7.1:** Navigate to the "History" page from the navigation.
        *   *Expected:* Workout History page is displayed. "Logged Workouts" table shows "Loading history...". Exercise filter dropdown is populated.
    *   **Step 7.2:** Wait for history to load.
        *   *Expected:* The workouts logged in section VI (e.g., Back Squat, Pull-up) are displayed in the table, ordered by most recent first. Each entry shows Date, Exercise Name, Sets, Reps, Weight.
    *   **Step 7.3 (Filtering):**
        *   **7.3.1:** Select "Back Squat" from the "Exercise Name" filter dropdown. Click "Apply Filters".
            *   *Expected:* Table updates to show only "Back Squat" logs.
        *   **7.3.2:** Select a date range that excludes the logged "Back Squat" workout. Click "Apply Filters".
            *   *Expected:* Table shows "No workouts logged yet or no results match your filters."
        *   **7.3.3:** Click "Reset Filters".
            *   *Expected:* All filters are cleared. Table reloads to show all logged workouts.
    *   **Step 7.4:** If no workouts have ever been logged.
        *   *Expected:* Page loads and shows "No workouts logged yet..." message.

## VI. General & Edge Cases

    *   **Step 8.1 (Navigation):** Click through all navigation links when logged in and logged out to ensure they lead to the correct pages and respect authentication.
        *   *Expected:* All links work. Attempting to access auth-required pages when logged out redirects to login.
    *   **Step 8.2 (Responsiveness - Basic Check):** Resize browser to a smaller width.
        *   *Expected:* Content should reflow reasonably. No major element overlaps or cut-offs (basic check, not expecting perfect mobile design).
    *   **Step 8.3 (API Access):** Attempt to access an API endpoint directly in the browser that requires login (e.g., `/api/user_maxes`) without being logged in.
        *   *Expected:* JSON error `{ "error": "Unauthorized" }` or redirect to login, depending on Flask-Login's default behavior for unauthenticated API access (which might be HTML redirect). For this app, it is likely a redirect to login.
    *   **Step 8.4 (Data Persistence):** After logging out and logging back in, verify that previously saved 1RMs and workout logs are still present.
        *   *Expected:* Data persists across sessions.

This checklist provides a good overview. Specific values (like weights, reps) can be adjusted by the tester.I have created the `manual_testing_checklist.md` file.

The unit test files (`test_models.py`, `test_program_generator.py`, `test_api_endpoints.py`) are already in the `tests` directory.

To ensure the tests can be run, one would typically execute `python -m unittest discover` from the project root directory (the one containing the `app` and `tests` folders). The `__init__.py` file in the `tests` directory helps with discovery.

The test setup in `tests/test_api_endpoints.py` includes creating an app context with a `TestConfig` that specifies an in-memory SQLite database (`sqlite:///:memory:`), ensuring that tests do not interfere with a development database and run in an isolated environment. `db.create_all()` is called in `setUp` and `db.drop_all()` in `tearDown` for each test class that needs database interaction.

The chosen unit tests cover:
1.  **`User` model password hashing:** `tests/test_models.py` checks `set_password` and `check_password`.
2.  **`program_generator.py` weight calculation:** `tests/test_program_generator.py` checks target weight calculation, rounding, and handling of missing 1RMs for the `generate_linear_program` function. This uses mocking for database dependencies.
3.  **`/api/log_workout` data validation:** `tests/test_api_endpoints.py` checks for successful logging, missing fields, invalid data types, non-existent exercises, and unauthorized access for the `/api/log_workout` endpoint.

All deliverables for this subtask are now complete.
