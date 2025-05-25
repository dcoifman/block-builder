from .models import UserMax, Exercise, db

# --- Program Structure Definition ---
PROGRAM_STRUCTURE = {
    "name": "4-Week Linear Periodization",
    "duration_weeks": 4,
    "days_per_week": 3,
    "weekly_intensity_progression": [ # % of 1RM for main lifts
        {"week": 1, "sets": 3, "reps": 8, "intensity_percent": 0.75},
        {"week": 2, "sets": 3, "reps": 6, "intensity_percent": 0.80},
        {"week": 3, "sets": 3, "reps": 4, "intensity_percent": 0.85},
        {"week": 4, "sets": 3, "reps": 5, "intensity_percent": 0.70} # Deload week, lighter
        # Alternative Week 4 (Peak): {"week": 4, "sets": 2, "reps": 3, "intensity_percent": 0.90}
    ],
    "daily_workouts": [
        { # Day 1
            "day_of_week": 1,
            "name": "Full Body A",
            "exercises": [
                {"name": "Back Squat", "type": "main"},
                {"name": "Bench Press", "type": "main"},
                {"name": "Barbell Row", "type": "main"},
                {"name": "Dumbbell Press", "type": "accessory", "sets": 3, "reps": "10-12"},
                {"name": "Bicep Curl", "type": "accessory", "sets": 3, "reps": "10-12"}
            ]
        },
        { # Day 2
            "day_of_week": 2,
            "name": "Full Body B",
            "exercises": [
                {"name": "Front Squat", "type": "main"}, # Could be Deadlift variation
                {"name": "Overhead Press", "type": "main"},
                {"name": "Chin-up", "type": "main"}, # Or Lat Pulldown
                {"name": "Tricep Extension", "type": "accessory", "sets": 3, "reps": "10-12"},
                {"name": "Hamstring Curl", "type": "accessory", "sets": 3, "reps": "10-12"}
            ]
        },
        { # Day 3
            "day_of_week": 3,
            "name": "Full Body C",
            "exercises": [
                {"name": "Deadlift", "type": "main"}, # Could be Back Squat variation
                {"name": "Incline Bench Press", "type": "main"}, # Or Bench Press variation
                {"name": "Barbell Row", "type": "main"}, # Pendlay Row or other variation
                {"name": "Lateral Raise", "type": "accessory", "sets": 3, "reps": "10-12"},
                {"name": "Calf Raise", "type": "accessory", "sets": 3, "reps": "10-12"}
            ]
        }
    ]
}

def generate_linear_program(user_id):
    generated_program = []
    user_maxes_query = UserMax.query.filter_by(user_id=user_id).all()
    user_1rms = {um.exercise.name: um.max_weight for um in user_maxes_query if um.exercise}

    # Verify all exercises in the program structure exist in the DB
    # This is important for data integrity. For simplicity, we assume exercises exist
    # or were added by populate-exercises script. A robust implementation would check here.

    for week_progression in PROGRAM_STRUCTURE["weekly_intensity_progression"]:
        week_num = week_progression["week"]
        main_lift_sets = week_progression["sets"]
        main_lift_reps = week_progression["reps"]
        main_lift_intensity = week_progression["intensity_percent"]

        for day_workout_template in PROGRAM_STRUCTURE["daily_workouts"]:
            day_num = day_workout_template["day_of_week"]

            for exercise_template in day_workout_template["exercises"]:
                exercise_name = exercise_template["name"]
                exercise_obj = Exercise.query.filter_by(name=exercise_name).first()

                if not exercise_obj:
                    # This exercise is in the program but not in DB. Skip or log.
                    # For MVP, we assume exercises are populated.
                    # In a real app, might add a placeholder or error.
                    generated_program.append({
                        "week": week_num,
                        "day": day_num,
                        "workout_name": day_workout_template["name"],
                        "exercise_name": exercise_name,
                        "exercise_type": exercise_template["type"],
                        "sets": "N/A",
                        "reps": "N/A",
                        "intensity_percent": "N/A",
                        "target_weight": "N/A",
                        "notes": f"Exercise '{exercise_name}' not found in database."
                    })
                    continue

                entry = {
                    "week": week_num,
                    "day": day_num,
                    "workout_name": day_workout_template["name"],
                    "exercise_name": exercise_name,
                    "exercise_type": exercise_template["type"],
                    "intensity_percent": None, # Default for accessories
                    "target_weight": None, # Default for accessories
                    "notes": ""
                }

                if exercise_template["type"] == "main":
                    entry["sets"] = main_lift_sets
                    entry["reps"] = main_lift_reps
                    entry["intensity_percent"] = main_lift_intensity * 100 # Store as percentage

                    if exercise_name in user_1rms:
                        user_1rm_for_exercise = user_1rms[exercise_name]
                        calculated_weight = user_1rm_for_exercise * main_lift_intensity
                        entry["target_weight"] = round(calculated_weight / 2.5) * 2.5 # Round to nearest 2.5 for common plates
                        if entry["target_weight"] == 0 and calculated_weight > 0 : # handle very small weights
                             entry["target_weight"] = 2.5 
                    else:
                        entry["target_weight"] = "1RM not set"
                        entry["notes"] = "User 1RM for this exercise is not set. Cannot calculate target weight."
                
                elif exercise_template["type"] == "accessory":
                    entry["sets"] = exercise_template["sets"]
                    entry["reps"] = exercise_template["reps"]
                    # Target weight for accessories is typically not based on 1RM in this simple model
                    entry["target_weight"] = "As prescribed / RPE based"
                    entry["notes"] = "Choose a weight that is challenging for the given rep range."
                
                generated_program.append(entry)

    return generated_program
