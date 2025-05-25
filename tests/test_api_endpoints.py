import unittest
import json
from app import create_app, db
from app.models import User, Exercise
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Use in-memory SQLite for tests
    WTF_CSRF_ENABLED = False # Disable CSRF for testing forms if any are used directly
    SECRET_KEY = 'test-secret-key'

class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app() # Using create_app from app/__init__.py
        self.app.config.from_object(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.create_test_user_and_exercise()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_test_user_and_exercise(self):
        # Create a test user
        self.test_user = User(username='testuser', email='test@example.com')
        self.test_user.set_password('password')
        db.session.add(self.test_user)
        
        # Create a test exercise
        self.test_exercise = Exercise(name='Test Squat', description='A test squat', primary_muscle_group='Legs')
        db.session.add(self.test_exercise)
        db.session.commit()

    def login_test_user(self):
        return self.client.post('/auth/login', data=dict(
            email='test@example.com',
            password='password'
        ), follow_redirects=True)

    # --- Tests for /api/log_workout ---
    def test_log_workout_success(self):
        self.login_test_user()
        response = self.client.post('/api/log_workout', json={
            'exercise_name': 'Test Squat',
            'sets': 3,
            'reps': 5,
            'weight': 100.5,
            'date_logged': '2023-01-15'
        })
        self.assertEqual(response.status_code, 201)
        json_response = response.get_json()
        self.assertEqual(json_response['message'], 'Workout logged successfully')
        self.assertEqual(json_response['exercise_name'], 'Test Squat')
        self.assertEqual(json_response['weight'], 100.5)

    def test_log_workout_missing_fields(self):
        self.login_test_user()
        response = self.client.post('/api/log_workout', json={
            'exercise_name': 'Test Squat',
            # 'sets': 3, # Missing sets
            'reps': 5,
            'weight': 100
        })
        self.assertEqual(response.status_code, 400)
        json_response = response.get_json()
        self.assertIn('Missing required field: sets', json_response['error'])

    def test_log_workout_invalid_data_type(self):
        self.login_test_user()
        response = self.client.post('/api/log_workout', json={
            'exercise_name': 'Test Squat',
            'sets': 'three', # Invalid type for sets
            'reps': 5,
            'weight': 100
        })
        self.assertEqual(response.status_code, 400)
        json_response = response.get_json()
        self.assertIn('Invalid value for sets, must be a positive integer', json_response['error'])

    def test_log_workout_negative_weight(self):
        self.login_test_user()
        response = self.client.post('/api/log_workout', json={
            'exercise_name': 'Test Squat',
            'sets': 3,
            'reps': 5,
            'weight': -50 # Invalid weight
        })
        self.assertEqual(response.status_code, 400)
        json_response = response.get_json()
        self.assertIn('Invalid value for weight, must be a non-negative number', json_response['error'])


    def test_log_workout_exercise_not_found(self):
        self.login_test_user()
        response = self.client.post('/api/log_workout', json={
            'exercise_name': 'Non Existent Exercise',
            'sets': 3,
            'reps': 5,
            'weight': 100
        })
        self.assertEqual(response.status_code, 404)
        json_response = response.get_json()
        self.assertIn("Exercise 'Non Existent Exercise' not found", json_response['error'])

    def test_log_workout_unauthorized(self):
        # No login
        response = self.client.post('/api/log_workout', json={
            'exercise_name': 'Test Squat',
            'sets': 3,
            'reps': 5,
            'weight': 100
        })
        # Expect redirect to login page for HTML, or 401 for pure API if configured
        # Given current setup, @login_required redirects to login URL which is an HTML response
        self.assertEqual(response.status_code, 302) # Redirect to login
        self.assertTrue('/auth/login' in response.location)


if __name__ == '__main__':
    unittest.main()
