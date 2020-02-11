import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.app.app_context().push()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        self.db.session.rollback()
        self.db.session.close()

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        response = self.client().get('/categories')
        self.assertEqual(response.status_code, 200)

    def test_get_questions(self):
        response = self.client().get('/questions')
        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(data['questions']), 10)

    def test_get_questions_with_query(self):
        response = self.client().get('/questions?page=2')
        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(data['questions']), 10)
        response = self.client().get('/questions?page=1&category=1')
        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(data['questions']), 10)

    def test_page_error_questions(self):
        response = self.client().get('/questions?page=1000000')
        self.assertEqual(response.status_code, 404)
        response = self.client().get('/questions?page=0')
        self.assertEqual(response.status_code, 404)
        response = self.client().get('/questions?page=-1')
        self.assertEqual(response.status_code, 404)

    def test_delete_question(self):
        dummy_question = Question(
            question='A?',
            answer='B',
            difficulty=1,
            category=1
        )
        dummy_question.insert()

        response = self.client().delete(f'/questions/{dummy_question.id}')
        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question_id'], str(dummy_question.id))

    def test_delete_wrong_question(self):
        response = self.client().delete('/questions/9999999999999')
        data = response.json
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_post_question(self):
        questions = Question.query.all()
        len_before = len(questions)

        response = self.client().post(
            '/questions',
            data=json.dumps(
                {
                    'question': 'A?',
                    'answer': 'B',
                    'difficulty': 1,
                    'category': 1,
                    'test': True
                }
            ),
            content_type='application/json'
        )
        data = response.json
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        questions = Question.query.all()
        len_after = len(questions)
        self.assertEqual(len_after, len_before + 1)

    def test_post_question_missing_attr(self):
        response = self.client().post(
            '/questions',
            data=json.dumps(
                {
                    'question': 'A?',
                    'difficulty': 1,
                    'test': True
                }
            ),
            content_type='application/json'
        )
        data = response.json
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_search_question(self):
        response = self.client().post(
            '/questions/search',
            data=json.dumps(
                {
                    'search_term': 'and'
                }
            ),
            content_type='application/json'
        )
        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_search_question_error(self):
        response = self.client().post(
            '/questions/search',
            data=json.dumps(
                {
                    'search_term': None
                }
            ),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 500)

    def test_get_question_by_category(self):
        response = self.client().get('/categories/2/questions')
        self.assertEqual(response.status_code, 200)

    def test_get_question_by_wrong_category(self):
        response = self.client().get('/categories/art/questions')
        self.assertEqual(response.status_code, 404)

    def test_quiz(self):
        response = self.client().post(
            '/quiz',
            data=json.dumps(
                {
                    'quiz_category': 1,
                    'previous_questions': []
                }
            ),
            content_type='application/json'
        )
        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_quiz_error(self):
        response = self.client().post(
            '/quiz',
            data=json.dumps(
                {
                    'quiz_category': 1
                }
            ),
            content_type='application/json'
        )
        data = response.json
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)

        response = self.client().post(
            '/quiz',
            data=json.dumps(
                {
                    'quiz_category': 'Art',
                    'previous_questions': []
                }
            ),
            content_type='application/json'
        )
        data = response.json
        self.assertEqual(response.status_code, 500)
        self.assertEqual(data['success'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
