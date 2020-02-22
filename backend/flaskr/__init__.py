from flask import Flask, request, abort, jsonify
from sqlalchemy import exc
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    db = setup_db(app)

    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response


    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        return jsonify(
            {
                'categories': {cat.id: cat.type for cat in categories}
            }
        ), 200

    
    @app.route('/questions')
    def get_questions():
        categories = Category.query.all()
        page = request.args.get('page', 1, type=int)
        current_category = request.args.get('category', None)

        page_questions, total_questions = Question.paginate(
            page,
            current_category
        )

        if len(page_questions) == 0 or page < 1:
            abort(404)

        return jsonify(
            {
                'success': True,
                'questions': page_questions,
                'total_questions': total_questions,
                'current_category': int(current_category),
                'categories': {cat.id: cat.type for cat in categories}
            }
        ), 200
    
    
    @app.route("/questions/<question_id>", methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            question.delete()
            success = True
            message = 'Successfully deleted'
            status_code = 200
        except exc.SQLAlchemyError:
            db.session.rollback()
            success = False
            message = 'Unable to delete question'
            status_code = 422
        return jsonify(
            {
                'success': success,
                'question_id': question_id,
                'message': message
            }
        ), status_code


    @app.route("/questions", methods=['POST'])
    def add_question():
        data = request.get_json()

        if any([
            attr not in data
            for attr in ['question', 'answer', 'difficulty', 'category']
        ]):
            return jsonify(
                {
                    'success': False,
                    'message':
                        "It's required to provide the question and answer "
                        "text, category (id), and difficulty score."
                }
            ), 422

        try:
            question = Question(
                question=data.get('question'),
                answer=data.get('answer'),
                difficulty=data.get('difficulty'),
                category=data.get('category')
            )

            test = data.get('test', False)
            question.insert(test)

            return jsonify(
                {
                    'success': True,
                    'question': question.format(),
                }
            ), 201

        except exc.SQLAlchemyError:
            abort(422)

            
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        data = request.get_json()
        search_term = data.get('search_term', None)

        categories = Category.query.all()

        if search_term:
            questions = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')
            ).all()

            return jsonify(
                {
                    'success': True,
                    'questions': [question.format() for question in questions],
                    'total_questions': len(questions),
                    'current_category': None,
                    'categories': {cat.id: cat.type for cat in categories}
                }
            ), 200
        abort(500)

        
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        try:
            questions = Question.query.filter_by(category=category_id).all()

            return jsonify(
                {
                    'success': True,
                    'questions': [question.format() for question in questions],
                    'total_questions': len(questions),
                    'current_category': category_id
                }
            ), 200
        except exc.SQLAlchemyError:
            abort(404)

            
    @app.route('/quiz', methods=['POST'])
    def play():
        try:
            data = request.get_json()

            if any([
                attr not in data
                for attr in ['quiz_category', 'previous_questions']
            ]):
                return jsonify(
                    {
                        'success': False,
                        'message': "It's required to provide the quiz_category "
                                   "and previous_questions."
                    }
                ), 422

            category = data.get('quiz_category')
            previous_questions = data.get('previous_questions', [])

            questions = Question.query.filter_by(
                category=category
            ).filter(Question.id.notin_(previous_questions)).all()

            if questions:
                question = random.choice(questions)

                return jsonify(
                    {
                        'success': True,
                        'question': question.format()
                    }
                )
            else:
                return jsonify(
                    {
                        'success': True,
                        'message': 'There are no more questions '
                                   'for this category.'
                    }
                )
        except exc.SQLAlchemyError:
            abort(500)

            
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify(
            {
                'success': False,
                'message': 'bad request',
                'error': 400
            }
        ), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify(
            {
                'success': False,
                'message': 'page not found',
                'error': 404
            }
        ), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify(
            {
                'success': False,
                'message': 'method not allowed',
                'error': 405
            }
        ), 405

    @app.errorhandler(422)
    def unprocessable(e):
        return jsonify(
            {
                'success': False,
                'message': 'Unprocessable',
                'error': 422
            }
        ), 422

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify(
            {
                'success': False,
                'message': 'internal error',
                'error': 500
            }
        ), 500

    return app
