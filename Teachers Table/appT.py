# appT.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import os
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///teachers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    level = db.Column(db.String(50))
    day = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'level': self.level,
            'day': self.day,
            'time': self.time,
            'email': self.email,
            'phone': self.phone
        }

class StudentAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)

def get_student_db_connection():
    student_db_path = os.path.join(os.path.dirname(__file__), 'test.db')
    return sqlite3.connect(student_db_path)

def get_students_from_registration():
    conn = get_student_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, level, day, time, email, phone FROM students")
            students = cursor.fetchall()
            return students
        except Exception as e:
            print(f"Error fetching students: {e}")
        finally:
            conn.close()
    return []


    
def get_all_students():
    conn = get_student_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT id, first_name || ' ' || last_name as name, level, day, time, email, phone FROM students")
        students = cur.fetchall()
        conn.close()
        return students
    return []



def get_students_for_teacher(teacher_id):
    assignments = StudentAssignment.query.filter_by(teacher_id=teacher_id).all()
    student_ids = [a.student_id for a in assignments]
    if not student_ids:
        return []

    conn = get_student_db_connection()
    if conn:
        placeholders = ','.join(['?'] * len(student_ids))
        query = f"SELECT id, name, level, day, time, email, phone FROM students WHERE id IN ({placeholders})"
        cur = conn.cursor()
        cur.execute(query, student_ids)
        students = cur.fetchall()
        conn.close()
        return students
    return []

def get_unassigned_students():
    all_students = get_all_students()
    assigned_ids = [a.student_id for a in StudentAssignment.query.all()]
    unassigned = [s for s in all_students if s[0] not in assigned_ids]  # s[0] is the student ID
    return unassigned


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        new_teacher = Teacher(
            name=request.form['name'],
            level=request.form['level'],
            day=request.form['day'],
            time=request.form['time'],
            email=request.form.get('email', ''),
            phone=request.form.get('phone', '')
        )
        db.session.add(new_teacher)
        db.session.commit()
        return redirect(url_for('index'))

    teachers = Teacher.query.order_by(Teacher.name).all()
    unassigned_students = get_unassigned_students()

    teacher_students = {}
    for teacher in teachers:
        teacher_students[teacher.id] = get_students_for_teacher(teacher.id)
    return render_template('indexT.html', teachers=teachers, unassigned_count=len(unassigned_students), teacher_students=teacher_students)

@app.route('/auto_assign', methods=['POST'])
def auto_assign():
    unassigned_students = get_unassigned_students()
    teachers = Teacher.query.all()
    if not teachers:
        return redirect(url_for('index'))
    for student in unassigned_students:
        assignment = StudentAssignment(
            student_id=student[0],
            teacher_id=random.choice(teachers).id
        )
        db.session.add(assignment)

    db.session.commit()
    return redirect(url_for('index'))

@app.route('/students/<int:teacher_id>')
def students_table(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    students = get_students_for_teacher(teacher_id)
    return render_template('students_table.html', teacher=teacher, students=students)


#APIS
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    Teacher.query.filter_by(id=id).delete()
    StudentAssignment.query.filter_by(teacher_id=id).delete()
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_assignment/<int:teacher_id>/<int:student_id>', methods=['POST'])
def delete_assignment(teacher_id, student_id):
    assignment = StudentAssignment.query.filter_by(teacher_id=teacher_id, student_id=student_id).first()
    if assignment:
        db.session.delete(assignment)
        db.session.commit()
    return redirect(url_for('students_table', teacher_id=teacher_id))


@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    teacher = Teacher.query.get(id)
    teacher.name = request.form['name']
    teacher.level = request.form['level']
    teacher.day = request.form['day']
    teacher.time = request.form['time']
    teacher.email = request.form.get('email', '')
    teacher.phone = request.form.get('phone', '')
    db.session.commit()
    return redirect(url_for('index'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
