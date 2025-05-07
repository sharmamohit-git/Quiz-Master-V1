from flask import Flask, redirect, render_template, request, url_for, session, flash
from app import app
from models import *

#------------------------------ROUTES-------------------------------





#===login====
@app.route('/', methods= ['GET','POST'])
def login():
    if request.method == 'POST':
        #retrieval of  user data from login html form
        username=request.form.get('username')
        password=request.form.get('password')

        #retrieval of user data from User table/class
        user=User.query.filter_by(username=username).first()

        #admin login
        if user and user.role_type == 0:
            if user.password == password:
                session['user_id'] = user.id
                flash('Login Successful','success')
                return redirect(url_for('admin_home'))
            flash('Wrong Credentials','danger')
            return redirect(url_for('login'))
        
        # user login
        elif user and user.role_type == 1:
            if user.password == password:
                session['user_id'] = user.id
                return redirect(f'/user_home/{user.id}')
            flash('Wrong Credentials','danger')
            return redirect(url_for('login'))
        else:
            flash('User does not exist','danger')
            return redirect(url_for('login'))
        
    
    return render_template('login.html')

#====signup====
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST': #to fetch details from html page form
        name = request.form.get('name').title()
        username = request.form.get('username')
        password = request.form.get('password')

        existing_user = User.query.filter_by(username=username).first() #to fetch details from User table in database
        if existing_user:
            flash('User already exists, use different username or login','info')
            return redirect(url_for('register'))
        new_user=User(name=name, username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registered successfully, please login','success')
        return redirect(url_for('login'))
        
    return render_template('register.html')



#====admin dashboard====ADMIN
@app.route('/admin_home')
def admin_home():
    if 'user_id' in session and session['user_id'] == 0:
        admin = User.query.filter_by(role_type=0).first()
        users = User.query.filter_by(role_type=1).all()
        subjects = Subject.query.all()
        chapters = Chapter.query.all()
        quizes = Quiz.query.all()

        return render_template('admin_home.html',users=users, subjects=subjects, admin=admin, chapters=chapters, quizes=quizes)
    flash('You are not logged in', 'warning')
    return redirect(url_for('login'))

#====user dashboard====USER
@app.route('/user_home')
def user_home():
    id=session['user_id']
    user=User.query.get(id)
    if 'user_id' in session and session['user_id']==id:
        quizes= Quiz.query.all()
        scores= Score.query.filter_by(user_id=id).all()
        return render_template('user_home.html', user=user, quizes=quizes, scores=scores)
    flash('You need to login to access this page','warning')
    return redirect(url_for('logout'))

#==========admin search=========#ADMIN
@app.route('/admin_home/search', methods= ['GET', 'POST'])
def admin_search():
    if 'user_id' in session and session['user_id'] == 0:
        search=request.form.get('search')
        if search:
            users= User.query.filter(User.name.ilike(f'%{search}%')).all()
            subjects= Subject.query.filter(Subject.name.ilike(f'%{search}%')).all()
            chapters= Chapter.query.filter(Chapter.name.ilike(f'%{search}%')).all()
            quizes= Quiz.query.filter(Quiz.name.ilike(f'%{search}%')).all()
            return render_template('admin_search_result.html', search=search, users=users, subjects=subjects, chapters=chapters, quizes=quizes)
        return render_template('admin_search_result.html', search='Nothing to search')
    flash('You are not logged in','warning')
    return redirect(url_for('logout'))



#========user search==========USER
@app.route('/user_home/search/<int:id>', methods= ['GET', 'POST'])
def user_search(id):
    if 'user_id' in session and session['user_id'] == id:
        search=request.form.get('search')
        if search:
            quizes= Quiz.query.filter(Quiz.name.ilike(f'%{search}%')).all()
            return render_template('user_search_result.html', search=search, quizes=quizes, user_id=id)
        return render_template('user_search_result.html', search='Nothing to search')
    flash('You are not logged in','warning')
    return redirect(url_for('logout'))


#====add new subject====
@app.route('/new_subject', methods= ['GET', 'POST']) #ADMIN
def new_subject():
    if 'user_id' in session and session['user_id'] == 0:
        if request.method=="POST":    
            subject_name = ((request.form.get('subject_name')).strip()).upper() #retrieve subject name from modal form
            subject_exist = Subject.query.filter_by(name=subject_name).first() # to check entered subject_name againt database
            if not subject_exist:
                add_subject = Subject(name=subject_name)
                db.session.add(add_subject)
                db.session.commit()
                flash('Subject added successfully','success')
                return redirect(url_for('admin_home'))
            flash('Subject already exists, enter different name','warning')
            return redirect(url_for('admin_home'))
        return render_template('new_subject.html')
    return redirect(url_for('logout'))

#====add new chapter====ADMIN    
@app.route('/new_chapter', methods= ['GET', 'POST']) #ADMIN
def new_chapter():
    if 'user_id' in session and session['user_id'] == 0:
        subjects=Subject.query.all()
        if request.method == 'POST':
            subject_id=request.form.get('selectsubject')
            chaptername=request.form.get('chaptername').strip().title()
            chapter= Chapter.query.filter_by(subject_id=subject_id, name=chaptername).first()
            if chapter:
                flash('Chapter already exists, enter different name','warning')
                return redirect(url_for('admin_home'))
            newchapter=Chapter(name=chaptername, subject_id=subject_id)
            db.session.add(newchapter)
            db.session.commit()
            flash('Chapter added successfully','success')
            return redirect(url_for('admin_home'))
        return render_template('new_chapter.html',subjects=subjects)
    return redirect(url_for('logout'))

#====add new quiz====ADMIN
@app.route('/new_quiz', methods= ['GET', 'POST']) #ADMIN
def new_quiz():
    if 'user_id' in session and session['user_id'] == 0:
        subjects=Subject.query.all()
        
        if request.method == 'POST':
            chapter_id=request.form.get('selectchapter')
            quizname=request.form.get('quizname').strip().title()
            
            quizes = Quiz.query.filter_by(chapter_id = chapter_id, name=quizname).first()
            if quizes:
                flash('Quiz already exists, enter different name','warning')
                return redirect(url_for('admin_home'))
            newquiz=Quiz(name=quizname, chapter_id=chapter_id)
            db.session.add(newquiz)
            db.session.commit()
            flash('Quiz added successfully','success')
            return redirect(url_for('admin_home'))
        return render_template('new_quiz.html',subjects=subjects) #page= new_quiz, variables= list of subjects
    flash('You are not logged in','warning')
    return redirect(url_for('logout'))



#=====add new Question=====ADMIN
@app.route('/new_question', methods= ['GET', 'POST']) #ADMIN
def new_question():
    if 'user_id' in session and session['user_id'] == 0:
        quizes=Quiz.query.all()
        if request.method == 'POST':
            selectquiz=request.form.get('selectquiz')
            question=request.form.get('question').strip()
            option1=request.form.get('option1').strip()
            option2=request.form.get('option2').strip()
            option3=request.form.get('option3').strip()
            option4=request.form.get('option4').strip()
            answer=request.form.get('answer').strip()
            new_question= Question(question=question, option1=option1, option2=option2, option3=option3, option4=option4, answer=answer, quiz_id=selectquiz)
            db.session.add(new_question)
            db.session.commit()
            flash('Question added successfully','success')
            return redirect(url_for('admin_home'))
        return render_template('new_question.html',quizes=quizes)
    return redirect(url_for('logout'))

#====edit subject details====ADMIN
@app.route('/edit_subject/<subject_name>/<int:subject_id>', methods= ['GET', 'POST']) #ADMIN
def edit_subject(subject_name, subject_id):
    if 'user_id' in session and session['user_id'] == 0:
        subject_details = Subject.query.filter_by(id=subject_id, name=subject_name).first()
        if not subject_details.id: 
            flash("Invalid subject")
            return redirect(url_for('admin_home'))
        if request.method == 'POST':
            subject_name = ((request.form.get('edit_subject')).strip()).upper()
            subject_name_exist = (Subject.query.filter_by(name=subject_name).first())
            if not subject_name_exist:
                subject_details.name = subject_name
                db.session.commit()
                flash('Updated successfully','success')
                return redirect(url_for('admin_home'))
            flash('Subject already exists','warning')
            return redirect(url_for('admin_home'))
        return render_template('edit_subject.html', subject_details=subject_details)
    return redirect(url_for('logout'))

#====edit chapter====ADMIN
@app.route('/edit_chapter/<chapter_name>/<int:chapter_id>', methods= ['GET', 'POST']) #ADMIN
def edit_chapter(chapter_name, chapter_id):
    if 'user_id' in session and session['user_id'] == 0:
        chapter_details = Chapter.query.filter_by(id=chapter_id).first() #returns one object
        if request.method == 'POST':
            chapter_name = ((request.form.get('edit_chapter')).strip()).title()
            chapter_details.name = chapter_name
            db.session.commit()
            flash('Updation Successful','success')
            return redirect(url_for('admin_home'))
        return render_template('edit_chapter.html', chapter_details=chapter_details)
    return redirect(url_for('logout'))

#====edit quiz====ADMIN
@app.route('/edit_quiz/<quiz_name>/<int:quiz_id>', methods= ['GET', 'POST']) #ADMIN
def edit_quiz(quiz_name, quiz_id):
    if 'user_id' in session and session['user_id'] == 0:
        quiz_details = Quiz.query.filter_by(id=quiz_id).first() #returns one object
        if request.method == 'POST':
            quiz_name = ((request.form.get('edit_quiz')).strip()).title()
            quiz_details.name = quiz_name
            db.session.commit()
            flash('Updation Successful','success')
            return redirect(f'/quiz_list/{quiz_details.belongstochapter.name}/{quiz_details.belongstochapter.id}')
        return render_template('edit_quiz.html', quiz_details=quiz_details)
    return redirect(url_for('logout'))

#====edit questions====ADMIN
@app.route('/edit_question/<int:question_id>', methods= ['GET', 'POST']) #ADMIN
def edit_question(question_id):
    if 'user_id' in session and session['user_id'] == 0:
        question_details = Question.query.filter_by(id=question_id).first() #returns one object
        if request.method == 'POST':
            #fetching existing data from form
            question = ((request.form.get('question')).strip())
            option1 = ((request.form.get('option1')).strip())
            option2 = ((request.form.get('option2')).strip())
            option3 = ((request.form.get('option3')).strip())
            option4 = ((request.form.get('option4')).strip())
            answer = ((request.form.get('answer')).strip())
            #updating in database
            question_details.question = question
            question_details.option1 = option1
            question_details.option2 = option2
            question_details.option3 = option3
            question_details.option4 = option4
            question_details.answer = answer
            db.session.commit()
            flash('Updation Successful','success')
            return redirect(f'/quiz/{question_details.belongstoquiz.name}/{question_details.belongstoquiz.id}')
        return render_template('edit_question.html', question_details=question_details, question_id=question_id)
    flash('You are not logged in','warning')
    return redirect(url_for('logout'))

#====delete a subject====ADMIN
@app.route('/delete_subject/<int:id>')
def delete_subject(id):
    if 'user_id' in session and session['user_id'] == 0:
        this_subject = Subject.query.get(id)
        db.session.delete(this_subject)
        db.session.commit()
        flash('Subject deleted','info')
        return redirect(url_for('admin_home'))
    return redirect(url_for('logout'))

#====delete chapter====ADMIN
@app.route('/delete_chapter/<int:id>')
def delete_chapter(id):
    if 'user_id' in session and session['user_id'] == 0:
        this_chapter = Chapter.query.get(id)
        db.session.delete(this_chapter)
        db.session.commit()
        flash('Chapter deleted','info')
        return redirect(url_for('admin_home'))
    return redirect(url_for('logout'))

#====delete quiz====ADMIN
@app.route('/delete_quiz/<chapter>/<int:chapter_id>/<quiz_name>/<int:id>')
def delete_quiz(chapter, chapter_id, quiz_name, id):
    if 'user_id' in session and session['user_id'] == 0:
        this_quiz = Quiz.query.get(id)
        db.session.delete(this_quiz)
        db.session.commit()
        flash('Quiz Deleted','info')
        return redirect(f'/quiz_list/{chapter}/{chapter_id}')
    return redirect(url_for('logout'))

#====delete question====ADMIN
@app.route('/delete_question/<quiz_name>/<int:quiz_id>/<int:question_id>', methods= ['GET', 'POST']) #ADMIN
def delete_question(quiz_id, quiz_name, question_id):
    if 'user_id' in session and session['user_id'] == 0:
        this_question=Question.query.filter_by(id=question_id).first()
        db.session.delete(this_question)
        db.session.commit()
        flash('Question deleted','info')
        return redirect(f'/quiz/{quiz_name}/{quiz_id}')
    return redirect(url_for('logout'))


#=====quiz list inside each chapter=====ADMIN
@app.route('/quiz_list/<chapter_name>/<int:chapter_id>')
def quiz_list(chapter_name,chapter_id):
    if 'user_id' in session and session['user_id'] == 0:
        quizes = Quiz.query.filter_by(chapter_id = chapter_id).all()
        return render_template('quiz_list.html', quizes=quizes, chapter_name=chapter_name)
    return redirect(url_for('logout'))

#=====quiz=====ADMIN
@app.route('/quiz/<quiz_name>/<int:quiz_id>') 
def quiz(quiz_name, quiz_id):
    if 'user_id' in session and session['user_id'] == 0:
        quiz=Quiz.query.filter_by(id=quiz_id).first()
        questions=Question.query.filter_by(quiz_id=quiz_id).all()
        return render_template('quiz.html',questions=questions, quiz=quiz, quiz_name=quiz_name, quiz_id=quiz_id)     
    return redirect(url_for('logout'))

#=====start quiz=====USER
@app.route('/user_<int:user_id>/start_quiz/quiz_<int:quiz_id>', methods= ['GET', 'POST'])
def start_quiz(user_id, quiz_id):
    if 'user_id' in session and session['user_id'] == user_id:
        questions=Question.query.filter_by(quiz_id=quiz_id).all()
        # score=Score.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
        return render_template('start_quiz.html', questions=questions, quiz_id=quiz_id, user_id=user_id)
    return redirect(url_for('logout'))

#=====quiz score=====USER
@app.route('/score/user_<int:user_id>/quiz_<int:quiz_id>', methods= ['GET', 'POST'])
def score(user_id, quiz_id):
    if 'user_id' in session and session['user_id'] == user_id:
        if request.method == 'POST':
            score = 0
            questions=Question.query.filter_by(quiz_id=quiz_id).all()
            for question in questions:
                response=request.form.get(str(question.id))
                myresponse= Response(response=response, question_id=question.id, user_id=user_id)
                db.session.add(myresponse)
                db.session.commit()
                if response == question.answer:
                    score = score + 1   
            myscore=Score(scored=score, user_id=user_id, quiz_id=quiz_id)
            db.session.add(myscore)
            db.session.commit()
            flash('Your responses have been submitted','info')
            return redirect(f'/user_home/{user_id}')
    flash('You need to login to access this page','warning')
    return redirect(url_for('logout'))

#==========view response==========USER
@app.route('/view_response/<int:quiz_id>/user/<int:user_id>') #put this link in view response button on user_home.html
def view_response(user_id, quiz_id):
    if 'user_id' in session and session['user_id'] == user_id:
        # questions= Question.query.filter_by(quiz_id=quiz_id, score_id=score_id).all()
        responses=Response.query.filter_by(user_id=user_id, quiz_id=quiz_id).all()
        return render_template('view_response.html', responses=responses)
    return redirect(url_for('logout'))


@app.route('/admin_summary')
def admin_summary():
    if 'user_id' in session and session['user_id'] == 0:
        subjects = Subject.query.all()

        # Create a list to hold quiz counts
        quiz_counts = []

        # Iterate through each subject and count quizzes
        for subject in subjects:
            quiz_count = sum(len(chapter.quizes) for chapter in subject.chapters)
            quiz_counts.append({
                'subject_name': subject.name,
                'quiz_count': quiz_count
            })

        # Return the data to the HTML template
        return render_template('admin_summary.html', quiz_counts=quiz_counts)
    return redirect(url_for('logout'))


@app.route('/user_<int:user_id>/summary')
def user_summary(user_id):
    if 'user_id' in session and session['user_id'] == user_id:
        scores = Score.query.filter_by(user_id=user_id).all()

        # Create a list of dictionaries with maximum score against corresponding quiz
        score_data = []
        for score in scores:
            if score.quiz_id not in [s['quiz_id'] for s in score_data]:
                max_score = Score.query.filter_by(user_id=user_id, quiz_id=score.quiz_id).order_by(Score.scored.desc()).first()
                score_data.append({'score': max_score.scored, 'quiz_name': score.belongstoquiz.name, 'quiz_id': score.quiz_id})

        # Return the data to the HTML template
        return render_template('user_summary.html', score_data=score_data, user_id=user_id) 
    return redirect(url_for('logout'))


@app.route('/logout')
def logout():
    flash('You are logged out','warning')
    session.clear()
    return redirect(url_for('login'))
