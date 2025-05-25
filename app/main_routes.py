from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import UserMax, Exercise, PoliquinRatio

# Blueprint for HTML serving pages
main_bp = Blueprint('main_bp', __name__)

# Blueprint for API endpoints
api_bp = Blueprint('api_bp', __name__, url_prefix='/api')


# --- HTML Page Routes (served by main_bp) ---

@main_bp.route('/')
def home_redirect():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.dashboard')) # Stays main_bp
    return redirect(url_for('auth.login')) # auth blueprint is separate

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@main_bp.route('/program')
@login_required
def view_program():
    return render_template('program.html') # Changed to render the actual program page

@main_bp.route('/log-workout-page')
@login_required
def log_workout_page():
    return render_template('placeholder_page.html', title="Log Workout", message="Workout logging form will be here.")

@main_bp.route('/history-page')
@login_required
def history_page():
    return render_template('history.html') # Changed to render the actual history page


# --- API Endpoints (served by api_bp, so they will be prefixed with /api) ---

@api_bp.route('/exercises', methods=['GET']) # Will be /api/exercises
@login_required
def get_all_exercises():
    exercises = Exercise.query.all()
    exercise_list = [{"id": ex.id, "name": ex.name} for ex in exercises]
    return jsonify(exercise_list)

@api_bp.route('/user_maxes', methods=['POST']) # Will be /api/user_maxes
@login_required
def add_or_update_user_max():
    data = request.get_json()
    if not data or 'exercise_name' not in data or 'max_weight' not in data:
        return jsonify({'error': 'Missing data: exercise_name and max_weight required'}), 400

    exercise_name = data['exercise_name']
    max_weight = data['max_weight']

    if not isinstance(max_weight, (int, float)) or max_weight <= 0:
        return jsonify({'error': 'Invalid max_weight: must be a positive number'}), 400

    exercise = Exercise.query.filter_by(name=exercise_name).first()
    if not exercise:
        return jsonify({'error': f'Exercise "{exercise_name}" not found'}), 404

    user_max = UserMax.query.filter_by(user_id=current_user.id, exercise_id=exercise.id).first() # Removed .first() here, will be added later

    if user_max:
        user_max.max_weight = max_weight
        user_max.date_recorded = db.func.current_timestamp() # Update timestamp
        status_message = 'User max updated successfully'
    else:
        user_max = UserMax(user_id=current_user.id, exercise_id=exercise.id, max_weight=max_weight)
        db.session.add(user_max)
        status_message = 'User max added successfully'

    try:
        db.session.commit()
        return jsonify({'message': status_message, 'id': user_max.id}), 201 if status_message.startswith('User max added') else 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database operation failed', 'details': str(e)}), 500

    user_max = UserMax.query.filter_by(user_id=current_user.id, exercise_id=exercise.id).first()

    if user_max:
        user_max.max_weight = max_weight
        user_max.date_recorded = db.func.current_timestamp() # Update timestamp
        status_message = 'User max updated successfully'
    else:
        user_max = UserMax(user_id=current_user.id, exercise_id=exercise.id, max_weight=max_weight)
        db.session.add(user_max)
        status_message = 'User max added successfully'

    try:
        db.session.commit()
        return jsonify({'message': status_message, 'id': user_max.id}), 201 if status_message.startswith('User max added') else 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database operation failed', 'details': str(e)}), 500

@api_bp.route('/user_maxes', methods=['GET']) # Will be /api/user_maxes
@login_required
def get_user_maxes():
    user_maxes = UserMax.query.filter_by(user_id=current_user.id).all()
    maxes_list = []
    for um in user_maxes:
        exercise = Exercise.query.get(um.exercise_id)
        maxes_list.append({
            'exercise_name': exercise.name if exercise else 'Unknown Exercise',
            'max_weight': um.max_weight,
            'date_recorded': um.date_recorded.isoformat()
        })
    return jsonify(maxes_list), 200

@api_bp.route('/poliquin_targets', methods=['GET']) # Will be /api/poliquin_targets
@login_required
def get_poliquin_targets():
    user_maxes_query = UserMax.query.filter_by(user_id=current_user.id).all()
    user_maxes = {um.exercise.name: um.max_weight for um in user_maxes_query if um.exercise}

    all_ratios = PoliquinRatio.query.all()
    targets = []

    for ratio_entry in all_ratios:
        primary_exercise_name = ratio_entry.primary_exercise_name
        secondary_exercise_name = ratio_entry.secondary_exercise_name
        ratio_value = ratio_entry.ratio

        if primary_exercise_name in user_maxes:
            primary_max_weight = user_maxes[primary_exercise_name]
            target_weight = primary_max_weight * ratio_value
            targets.append({
                'secondary_exercise_name': secondary_exercise_name,
                'target_weight': round(target_weight, 2), # Round to 2 decimal places
                'primary_exercise_name_used': primary_exercise_name,
                'primary_exercise_max_used': primary_max_weight,
                'ratio_applied': ratio_value
            })
    return jsonify(targets), 200

from .program_generator import generate_linear_program

@api_bp.route('/program/generate_linear', methods=['GET']) # Will be /api/program/generate_linear
@login_required
def get_generated_linear_program():
    """
    Generates a 4-week linear periodization program for the current user
    based on their stored 1RMs.
    """
    program = generate_linear_program(current_user.id)
    if not program:
        return jsonify({"error": "Could not generate program. User may not have 1RMs set for program exercises or program structure is incomplete."}), 500
    
    return jsonify(program), 200

from datetime import datetime

@api_bp.route('/log_workout', methods=['POST']) # Will be /api/log_workout
@login_required
def log_workout_entry():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input, no data provided"}), 400

    required_fields = ['exercise_name', 'sets', 'reps', 'weight']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    exercise_name = data['exercise_name']
    sets = data['sets']
    reps = data['reps']
    weight = data['weight']
    date_logged_str = data.get('date_logged') # Optional

    # Validate data types
    if not isinstance(exercise_name, str):
        return jsonify({"error": "Invalid type for exercise_name, must be string"}), 400
    if not isinstance(sets, int) or sets <= 0:
        return jsonify({"error": "Invalid value for sets, must be a positive integer"}), 400
    if not isinstance(reps, int) or reps <= 0:
        return jsonify({"error": "Invalid value for reps, must be a positive integer"}), 400
    if not isinstance(weight, (int, float)) or weight < 0: # Weight can be 0 for bodyweight exercises if logged that way
        return jsonify({"error": "Invalid value for weight, must be a non-negative number"}), 400

    exercise = Exercise.query.filter_by(name=exercise_name).first()
    if not exercise:
        return jsonify({"error": f"Exercise '{exercise_name}' not found"}), 404

    date_logged_obj = datetime.utcnow()
    if date_logged_str:
        try:
            date_logged_obj = datetime.strptime(date_logged_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try: # Attempt to parse just date if time is not provided
                date_logged_obj = datetime.strptime(date_logged_str, '%Y-%m-%d')
            except ValueError:
                return jsonify({"error": "Invalid date_logged format. Use YYYY-MM-DD HH:MM:SS or YYYY-MM-DD"}), 400
    
    new_log = WorkoutLog(
        user_id=current_user.id,
        exercise_id=exercise.id,
        sets=sets,
        reps=reps,
        weight=weight,
        date_logged=date_logged_obj
    )

    try:
        db.session.add(new_log)
        db.session.commit()
        return jsonify({
            "message": "Workout logged successfully",
            "log_id": new_log.id,
            "exercise_name": exercise.name,
            "sets": new_log.sets,
            "reps": new_log.reps,
            "weight": new_log.weight,
            "date_logged": new_log.date_logged.isoformat()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to log workout", "details": str(e)}), 500

@main_bp.route('/workout_history', methods=['GET']) # Original route was /api/workout_history
@login_required
def get_workout_history():
    # Basic query parameters for filtering (optional for now, but good to have basic structure)
    exercise_name_filter = request.args.get('exercise_name')
    date_from_filter_str = request.args.get('date_from') # Expected format YYYY-MM-DD
    date_to_filter_str = request.args.get('date_to')     # Expected format YYYY-MM-DD

    query = WorkoutLog.query.filter_by(user_id=current_user.id)

    if exercise_name_filter:
        exercise = Exercise.query.filter_by(name=exercise_name_filter).first()
        if exercise:
            query = query.filter_by(exercise_id=exercise.id)
        else:
            return jsonify({"error": f"Exercise '{exercise_name_filter}' not found for filtering"}), 404
    
    if date_from_filter_str:
        try:
            date_from = datetime.strptime(date_from_filter_str, '%Y-%m-%d')
            query = query.filter(WorkoutLog.date_logged >= date_from)
        except ValueError:
            return jsonify({"error": "Invalid date_from format. Use YYYY-MM-DD"}), 400
            
    if date_to_filter_str:
        try:
            date_to = datetime.strptime(date_to_filter_str, '%Y-%m-%d')
            # To make the range inclusive for the 'to' date, we can adjust it to end of day
            from datetime import time
            date_to = datetime.combine(date_to, time.max)
            query = query.filter(WorkoutLog.date_logged <= date_to)
        except ValueError:
            return jsonify({"error": "Invalid date_to format. Use YYYY-MM-DD"}), 400

    logs = query.order_by(WorkoutLog.date_logged.desc()).all()
    
    history_list = []
    for log in logs:
        exercise = Exercise.query.get(log.exercise_id) # Could also use join in the main query for efficiency
        history_list.append({
            "log_id": log.id,
            "exercise_name": exercise.name if exercise else "Unknown Exercise",
            "sets": log.sets,
            "reps": log.reps,
            "weight": log.weight,
            "date_logged": log.date_logged.isoformat()
        })
    return jsonify(history_list), 200
