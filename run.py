from app import app, db # Import db from app

@app.cli.command("init-db")
def init_db_command():
    """Creates the database tables."""
    with app.app_context():
        db.create_all()
    print("Initialized the database.")

@app.cli.command("populate-exercises")
def populate_exercises_command():
    """Populates the Exercise table with initial data."""
    with app.app_context():
        from app.models import Exercise
        exercises_data = [
            # Compound Lifts
            {"name": "Back Squat", "primary_muscle_group": "Quads, Glutes, Hamstrings", "description": "A fundamental lower body exercise."},
            {"name": "Front Squat", "primary_muscle_group": "Quads, Core", "description": "A squat variation emphasizing quads and core."},
            {"name": "Bench Press", "primary_muscle_group": "Chest, Triceps, Shoulders", "description": "A fundamental upper body pressing exercise."},
            {"name": "Close Grip Bench Press", "primary_muscle_group": "Triceps, Chest", "description": "A bench press variation emphasizing triceps."},
            {"name": "Overhead Press", "primary_muscle_group": "Shoulders, Triceps", "description": "An upper body exercise pressing weight overhead."},
            {"name": "Deadlift", "primary_muscle_group": "Back, Glutes, Hamstrings, Quads", "description": "A full-body exercise lifting weight from the floor."},
            {"name": "Barbell Row", "primary_muscle_group": "Back, Biceps", "description": "An upper body exercise pulling weight towards the torso."},
            {"name": "Chin-up", "primary_muscle_group": "Back, Biceps", "description": "An upper body exercise pulling the body up using an underhand grip."},
            {"name": "Pull-up", "primary_muscle_group": "Back, Biceps", "description": "An upper body exercise pulling the body up using an overhand grip."},
            {"name": "Incline Bench Press", "primary_muscle_group": "Upper Chest, Shoulders, Triceps", "description": "Bench press on an incline, typically with a barbell."},
            # Accessory Exercises
            {"name": "Dumbbell Press", "primary_muscle_group": "Chest, Shoulders, Triceps", "description": "A pressing exercise using dumbbells."},
            {"name": "Incline Dumbbell Press", "primary_muscle_group": "Upper Chest, Shoulders, Triceps", "description": "An incline pressing exercise using dumbbells."},
            {"name": "Bicep Curl", "primary_muscle_group": "Biceps", "description": "An isolation exercise for the biceps."},
            {"name": "Tricep Extension", "primary_muscle_group": "Triceps", "description": "An isolation exercise for the triceps."},
            {"name": "Leg Press", "primary_muscle_group": "Quads, Glutes, Hamstrings", "description": "A lower body exercise using a leg press machine."},
            {"name": "Calf Raise", "primary_muscle_group": "Calves", "description": "An isolation exercise for the calves."},
            {"name": "Lateral Raise", "primary_muscle_group": "Shoulders (Lateral Head)", "description": "An isolation exercise for the side deltoids."},
            {"name": "Hamstring Curl", "primary_muscle_group": "Hamstrings", "description": "An isolation exercise for the hamstrings."},
            {"name": "Leg Extension", "primary_muscle_group": "Quads", "description": "An isolation exercise for the quads."},
            {"name": "Chest Fly", "primary_muscle_group": "Chest", "description": "An isolation exercise for the chest using dumbbells or cables."},
            {"name": "Romanian Deadlift", "primary_muscle_group": "Hamstrings, Glutes, Lower Back", "description": "A deadlift variation focusing on hamstrings and glutes."}
        ]
        for ex_data in exercises_data:
            if not Exercise.query.filter_by(name=ex_data["name"]).first():
                exercise = Exercise(name=ex_data["name"], primary_muscle_group=ex_data["primary_muscle_group"], description=ex_data["description"])
                db.session.add(exercise)
        db.session.commit()
        print("Populated exercises.")

@app.cli.command("populate-ratios")
def populate_ratios_command():
    """Populates the PoliquinRatio table with initial data."""
    with app.app_context():
        from app.models import PoliquinRatio, Exercise
        ratios_data = [
            {"primary": "Back Squat", "secondary": "Front Squat", "ratio": 0.85},
            {"primary": "Bench Press", "secondary": "Close Grip Bench Press", "ratio": 0.90},
            {"primary": "Bench Press", "secondary": "Incline Bench Press", "ratio": 0.80}, # Example, assuming Incline Bench Press exists
            {"primary": "Bench Press", "secondary": "Overhead Press", "ratio": 0.60}, # Example, assuming OHP exists
            {"primary": "Deadlift", "secondary": "Romanian Deadlift", "ratio": 0.80}
        ]

        # Ensure "Incline Bench Press" exercise exists for the ratio
        incline_bp_name = "Incline Bench Press"
        if not Exercise.query.filter_by(name=incline_bp_name).first():
            incline_bp = Exercise(name=incline_bp_name, primary_muscle_group="Upper Chest, Shoulders", description="Bench press on an incline.")
            db.session.add(incline_bp)
            print(f"Added missing exercise: {incline_bp_name}")

        for ratio_data in ratios_data:
            # Check if primary and secondary exercises exist
            primary_ex = Exercise.query.filter_by(name=ratio_data["primary"]).first()
            secondary_ex = Exercise.query.filter_by(name=ratio_data["secondary"]).first()

            if not primary_ex:
                print(f"Warning: Primary exercise '{ratio_data['primary']}' for ratio not found. Skipping ratio.")
                continue
            if not secondary_ex:
                print(f"Warning: Secondary exercise '{ratio_data['secondary']}' for ratio not found. Skipping ratio.")
                continue

            if not PoliquinRatio.query.filter_by(primary_exercise_name=ratio_data["primary"], secondary_exercise_name=ratio_data["secondary"]).first():
                ratio_entry = PoliquinRatio(
                    primary_exercise_name=ratio_data["primary"],
                    secondary_exercise_name=ratio_data["secondary"],
                    ratio=ratio_data["ratio"]
                )
                db.session.add(ratio_entry)
        db.session.commit()
        print("Populated Poliquin ratios.")

if __name__ == '__main__':
    app.run(debug=True)
