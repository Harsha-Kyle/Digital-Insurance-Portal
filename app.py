# run: app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY','super-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///insurance.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

from models import User, Policy, Application, Claim
db.create_all()

# --- AUTH ROUTES ---
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        u=User.query.filter_by(email=request.form['email']).first()
        if u and u.password==request.form['password']:
            session['user_id']=u.id; return redirect('/')
        flash('Invalid credentials'); 
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id',None)
    return redirect('/login')

# --- MAIN DASHBOARD ---
@app.route('/')
def home():
    if 'user_id' not in session: return redirect('/login')
    return render_template('index.html')

# --- POLICIES & APPLICATION ---
@app.route('/policies')
def policies():
    if 'user_id' not in session: return redirect('/login')
    return render_template('policies.html', policies=Policy.query.all())

@app.route('/apply/<int:policy_id>', methods=['GET','POST'])
def apply(policy_id):
    if 'user_id' not in session: return redirect('/login')
    p=Policy.query.get_or_404(policy_id)
    if request.method=='POST':
        appn=Application(user_id=session['user_id'], policy_id=policy_id,
                         term=request.form['term'], premium=float(p.premium))
        db.session.add(appn); db.session.commit()
        flash('Applied successfully'); return redirect('/claims')
    return render_template('apply.html', policy=p)

# --- CLAIMS ---
@app.route('/claims', methods=['GET','POST'])
def claims():
    if 'user_id' not in session: return redirect('/login')
    if request.method=='POST':
        f=request.files['file']
        fname = datetime.utcnow().strftime("%Y%m%d%H%M%S_") + f.filename
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
        cl=Claim(user_id=session['user_id'], details=request.form['details'], file=fname)
        db.session.add(cl); db.session.commit()
        flash('Claim filed')
    cls=Claim.query.filter_by(user_id=session['user_id']).all()
    return render_template('claims.html', claims=cls)

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT',5000)))
