from flask import Flask, render_template, redirect, url_for, session, request
import jinja2


app=Flask(__name__)

app.config['SECRET_KEY'] = '23quizmasterv1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from models import *
db.init_app(app)

with app.app_context():
    db.create_all()
    new_admin= User.query.filter_by(role_type=0).first()
    if not new_admin:
        admin = User(id=0, name='Administrator', username='admin', password='012345', role_type=0)
        db.session.add(admin)
        db.session.commit()
    


from routes import *


if __name__=='__main__':
    app.run(debug=True) #Default port is 5000, we can change it to 8080
