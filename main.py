from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///university.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    id_number = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(50))
    email = db.Column(db.String(50))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password!')
    return render_template('login.html')

@app.route('/')
@login_required
def dashboard():
    total_students = Student.query.count()
    return render_template('dashboard.html', total=total_students)

@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        id_num = request.form.get('id_number')
        if Student.query.filter_by(id_number=id_num).first():
            flash('This ID number is already registered!')
        else:
            new_student = Student(
                full_name=request.form.get('full_name'),
                id_number=id_num,
                department=request.form.get('department'),
                email=request.form.get('email')
            )
            db.session.add(new_student)
            db.session.commit()
            flash('Student registered successfully!')
    return render_template('add_student.html')

@app.route('/students')
@login_required
def list_students():
    query = request.args.get('id_number')
    if query:
        students = Student.query.filter(Student.id_number.contains(query)).all()
    else:
        students = Student.query.all()
    return render_template('students.html', students=students)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        student.full_name = request.form.get('full_name')
        student.department = request.form.get('department')
        db.session.commit()
        flash('Student updated successfully!')
        return redirect(url_for('list_students'))
    return render_template('edit_student.html', student=student)

@app.route('/delete/<int:id>')
@login_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully!')
    return redirect(url_for('list_students'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)