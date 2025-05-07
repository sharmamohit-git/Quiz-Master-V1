from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime


db = SQLAlchemy()



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    username = db.Column(db.String(10), unique=True, nullable=False)
    password = db.Column(db.String(10), nullable=False)
    role_type = db.Column(db.Integer, nullable=False, default=1) # for admin role_type = 0


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)

    chapters = db.relationship('Chapter', backref='belongstosubject', cascade='all, delete-orphan')

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))

    quizes = db.relationship('Quiz', backref='belongstochapter', cascade='all, delete')

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), default='Quiz')
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable= False)

    questions = db.relationship('Question', backref='belongstoquiz', cascade='all, delete')
    scores = db.relationship('Score', backref='belongstoquiz', cascade='all, delete')

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text)
    option1 = db.Column(db.Text)
    option2 = db.Column(db.Text)
    option3 = db.Column(db.Text)
    option4 = db.Column(db.Text)
    answer = db.Column(db.Text)

    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    responses = db.relationship('Response', backref='belongstoquestion', cascade='all, delete')
    
class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    response = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    score_id = db.Column(db.Integer, db.ForeignKey('score.id'))
    
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scored = db.Column(db.Integer)
    date_of_attempt = db.Column(db.DateTime, nullable= False, default= func.now())

    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    responses= db.relationship('Response', backref='belongtoscore', cascade='all, delete')
 

