import unittest
from unittest.mock import MagicMock, patch
from app.program_generator import generate_linear_program, PROGRAM_STRUCTURE
# To make this testable, we need to be able to mock the database queries.
# We'll assume that Exercise and UserMax models can be mocked.

# Mock classes for models
class MockExercise:
    def __init__(self, name, id):
        self.name = name
        self.id = id

class MockUserMax:
    def __init__(self, exercise_name, max_weight, exercise_id):
        self.exercise = MockExercise(name=exercise_name, id=exercise_id)
        self.max_weight = max_weight

class TestProgramGenerator(unittest.TestCase):

    @patch('app.program_generator.UserMax.query')
    @patch('app.program_generator.Exercise.query')
    def test_generate_linear_program_weight_calculation_and_rounding(self, mock_exercise_query, mock_user_max_query):
        # --- Setup Mocks ---
        # Mock Exercise.query.filter_by().first()
        # This needs to return a MockExercise object for each exercise name in PROGRAM_STRUCTURE
        def mock_exercise_filter_by_side_effect(name):
            # Simplified: assume all exercises in program structure exist and have an ID
            exercise_map = {ex["name"]: MockExercise(name=ex["name"], id=idx+1) 
                            for idx, ex_list in enumerate(PROGRAM_STRUCTURE["daily_workouts"]) 
                            for ex in ex_list["exercises"]}
            return MagicMock(first=MagicMock(return_value=exercise_map.get(name)))

        mock_exercise_query.filter_by = MagicMock(side_effect=mock_exercise_filter_by_side_effect)
        
        # Mock UserMax.query.filter_by().all()
        # Let's say user has 1RM for Back Squat = 100kg and Bench Press = 70kg
        user_maxes_data = [
            MockUserMax(exercise_name="Back Squat", max_weight=100, exercise_id=1), # Assume ID 1
            MockUserMax(exercise_name="Bench Press", max_weight=70, exercise_id=2),  # Assume ID 2
        ]
        mock_user_max_query.filter_by.return_value = MagicMock(all=MagicMock(return_value=user_maxes_data))
        
        user_id = 1 # Dummy user_id
        program = generate_linear_program(user_id)

        # --- Assertions ---
        self.assertTrue(len(program) > 0, "Program should not be empty")

        found_back_squat_week1 = False
        found_bench_press_week1 = False
        found_other_main_lift_no_1rm = False
        found_accessory_lift = False

        for entry in program:
            # Test Back Squat in Week 1 (75% of 100kg = 75kg)
            if entry["exercise_name"] == "Back Squat" and entry["week"] == 1 and entry["type"] == "main":
                found_back_squat_week1 = True
                self.assertEqual(entry["intensity_percent"], 75.0)
                self.assertEqual(entry["target_weight"], 75.0) # 100 * 0.75 = 75.0 (rounds to 75.0)
            
            # Test Bench Press in Week 1 (75% of 70kg = 52.5kg)
            if entry["exercise_name"] == "Bench Press" and entry["week"] == 1 and entry["type"] == "main":
                found_bench_press_week1 = True
                self.assertEqual(entry["intensity_percent"], 75.0)
                self.assertEqual(entry["target_weight"], 52.5) # 70 * 0.75 = 52.5 (rounds to 52.5)

            # Test a main lift where 1RM is NOT set (e.g., Barbell Row if it's main)
            if entry["exercise_name"] == "Barbell Row" and entry["type"] == "main" and entry["week"] == 1:
                # Assuming Barbell Row is in PROGRAM_STRUCTURE and is a main lift, and no 1RM was provided for it
                found_other_main_lift_no_1rm = True
                self.assertEqual(entry["target_weight"], "1RM not set")
                self.assertIn("1RM for this exercise is not set", entry["notes"])

            # Test an accessory lift (e.g., Dumbbell Press)
            if entry["exercise_name"] == "Dumbbell Press" and entry["type"] == "accessory":
                found_accessory_lift = True
                self.assertEqual(entry["target_weight"], "As prescribed / RPE based")
                self.assertIsNone(entry["intensity_percent"]) # No intensity % for accessories in this model

        self.assertTrue(found_back_squat_week1, "Week 1 Back Squat not found in program")
        self.assertTrue(found_bench_press_week1, "Week 1 Bench Press not found in program")
        self.assertTrue(found_other_main_lift_no_1rm, "Test for main lift without 1RM not triggered")
        self.assertTrue(found_accessory_lift, "Test for accessory lift not triggered")

    @patch('app.program_generator.UserMax.query')
    @patch('app.program_generator.Exercise.query')
    def test_weight_rounding(self, mock_exercise_query, mock_user_max_query):
        # Mock Exercise.query (same as above, simplified)
        exercise_map = {ex["name"]: MockExercise(name=ex["name"], id=idx+1) 
                        for idx, ex_list in enumerate(PROGRAM_STRUCTURE["daily_workouts"]) 
                        for ex in ex_list["exercises"]}
        mock_exercise_query.filter_by = MagicMock(side_effect=lambda name: MagicMock(first=MagicMock(return_value=exercise_map.get(name))))

        # UserMax for Back Squat: 101kg. Week 1: 75% of 101 = 75.75. Rounded = 75.0 (as per current rounding)
        # Let's adjust the rounding logic in program_generator to be more standard (round to nearest 2.5)
        # Current logic: round(calculated_weight / 2.5) * 2.5. For 75.75: round(30.3)*2.5 = 30*2.5 = 75.0
        # Let's test another: 102kg. Week 1: 75% of 102 = 76.5. round(76.5/2.5)*2.5 = round(30.6)*2.5 = 31*2.5 = 77.5
        user_maxes_data = [MockUserMax(exercise_name="Back Squat", max_weight=102, exercise_id=1)]
        mock_user_max_query.filter_by.return_value = MagicMock(all=MagicMock(return_value=user_maxes_data))

        program = generate_linear_program(1)
        
        back_squat_week1_weight = None
        for entry in program:
            if entry["exercise_name"] == "Back Squat" and entry["week"] == 1 and entry["type"] == "main":
                back_squat_week1_weight = entry["target_weight"]
                break
        
        self.assertIsNotNone(back_squat_week1_weight, "Back Squat Week 1 entry not found")
        self.assertEqual(back_squat_week1_weight, 77.5) # 102 * 0.75 = 76.5. round(76.5/2.5)*2.5 = round(30.6)*2.5 = 31*2.5 = 77.5

if __name__ == '__main__':
    unittest.main()
