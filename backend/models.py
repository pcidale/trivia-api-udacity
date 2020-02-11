import os
from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy


database_name = "trivia"
database_path = "postgres://{}/{}".format('localhost:5432', database_name)

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()
    return db

'''
Question

'''


class Question(db.Model):  
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)
    category = Column(Integer)
    difficulty = Column(Integer)

    def __init__(self, question, answer, category, difficulty):
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = difficulty

    def insert(self, test=False):
        db.session.add(self)
        if not test:
            db.session.commit()
  
    def update(self):
       db.session.commit()

    def delete(self, test=False):
        db.session.delete(self)
        if not test:
            db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'difficulty': self.difficulty
        }

    @staticmethod
    def paginate(page, current_category=None):
        if current_category:
            questions = Question.query.filter_by(
                category=current_category
            ).order_by(Question.id).all()
        else:
            questions = Question.query.order_by(Question.id).all()

        start = (page - 1) * 10
        end = start + 10
        page_questions = questions[start:end]
        return ([question.format() for question in page_questions],
                len(questions))


'''
Category

'''


class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(String)

    def __init__(self, type):
        self.type = type

    def format(self):
        return {
            'id': self.id,
            'type': self.type
        }
