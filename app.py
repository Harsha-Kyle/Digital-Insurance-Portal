from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'super-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///insurance.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

class Policy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    type = db.Column(db.String(50))
    premium = db.Column(db.Float)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    policy_id = db.Column(db.Integer, db.ForeignKey('policy.id'))
    term = db.Column(db.String(50))
    premium = db.Column(db.Float)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

class Claim(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    details = db.Column(db.Text)
    file = db.Column(db.String(200))
    filed_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='Submitted')

# Routes
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if User.query.filter_by(email=request.form['email']).first():
            flash('Email already registered')
        else:
            u = User(email=request.form['email'], password=request.form['password'])
            db.session.add(u)
            db.session.commit()
            flash('Registered! Please login.')
            return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = User.query.filter_by(email=request.form['email']).first()
        if u and u.password == request.form['password']:
            session['user_id'] = u.id
            return redirect('/')
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')

@app.route('/policies')
def policies():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('policies.html', policies=Policy.query.all())

@app.route('/apply/<int:policy_id>', methods=['GET', 'POST'])
def apply(policy_id):
    if 'user_id' not in session:
        return redirect('/login')
    p = Policy.query.get_or_404(policy_id)
    if request.method == 'POST':
        appn = Application(user_id=session['user_id'], policy_id=policy_id,
                           term=request.form['term'], premium=p.premium)
        db.session.add(appn)
        db.session.commit()
        flash('Applied successfully')
        return redirect('/claims')
    return render_template('apply.html', policy=p)

@app.route('/claims', methods=['GET', 'POST'])
def claims():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        f = request.files['file']
        fname = datetime.utcnow().strftime("%Y%m%d%H%M%S_") + f.filename
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
        cl = Claim(user_id=session['user_id'], details=request.form['details'], file=fname)
        db.session.add(cl)
        db.session.commit()
        flash('Claim filed')
    cls = Claim.query.filter_by(user_id=session['user_id']).all()
    return render_template('claims.html', claims=cls)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Policy.query.first():
            db.session.add_all([
                Policy(name="Health Secure", type="Health", premium=3000),
                Policy(name="Life Plus", type="Life", premium=4500),
                Policy(name="Vehicle Shield", type="Vehicle", premium=5000),
            ])
            db.session.commit()
    app.run(debug=True)
