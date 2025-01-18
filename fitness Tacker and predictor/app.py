from flask import Flask, render_template, request, redirect, session
import os
from train_model import calculate_calories  # Ensure this is the correct import
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitness.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app) #instance 

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

# instance folder 
if not os.path.exists('instance'):
    os.makedirs('instance/files', exist_ok=True)
if not os.path.exists('instance/fitness.db'):
    with app.app_context():
        db.create_all()

@app.route('/')
def home():
    if 'username' in session:
        return redirect('/login')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = username
            return redirect('/index')
        return 'Invalid credentials!'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return 'User already exists!'
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        os.makedirs(os.path.join('instance/files', username), exist_ok=True)
        return redirect('/login')
    return render_template('register.html')

@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect('/')
    
    activities = session.get('activities', [])

    if request.method == 'POST':
        activity = request.form['activity']
        weight = float(request.form['weight'])
        duration = float(request.form['duration'])
        
        calories = calculate_calories(activity, weight, duration)
        
        new_activity = {
            'activity': activity,
            'weight': weight,
            'duration': duration,
            'calories': calories
        }
        activities.append(new_activity)
        session['activities'] = activities

        avg_calories = sum([a['calories'] for a in activities]) / len(activities) if activities else 0
        return render_template('index.html', prediction=calories, activities=activities, avg_calories=avg_calories)

    avg_calories = sum([a['calories'] for a in activities]) / len(activities) if activities else 0
    return render_template('index.html', activities=activities, avg_calories=avg_calories)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('actiavities', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
