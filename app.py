#enter environment - .\env\Scripts\activate 
#INITIALIZE DATABASE ---> python -c "from app import 
# app, db; app.app_context().push(); db.create_all(); print('Database initialized')"
from flask import Flask, render_template, request, redirect, url_for
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) #initialize database
migrate = Migrate(app, db)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    student_id = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(50), unique=True)
    parents_full_name = db.Column(db.String(50), nullable = False)
    age = db.Column(db.String(2), nullable = False)
    address = db.Column(db.String(20), nullable = False)
    phone_number =db.Column(db.String(10), nullable = False)
    courses =db.Column(db.String(10), nullable = False)
    teacher = db.Column(db.String(100))



#doesnt do anything cuz i deleted the date field in the Student class ^^^
def to_dict(self):
    return {
        'id': self.id,
        'first_name': self.first_name,
        'last_name': self.last_name,
        'student_id': self.student_id,
        'email': self.email,
        'parents_full_name': self.parents_full_name,
        'age': self.age,
        'address': self.address
    }
        


#display and process form
@app.route('/', methods=['GET', 'POST'])
def index():
    #post resquest (form submission)
    if request.method == 'POST':
        duplicate = Student.query.filter(
            (Student.student_id ==request.form['student_id']) |
            (Student.email==request.form['email']) 
        ).first()

        if duplicate:
            students = Student.query.all()
            return render_template('index.html', students=students, duplicate_exists = True)
        try: 
            new_student = Student(
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                student_id=request.form['student_id'],
                email=request.form['email'],
                parents_full_name=request.form['parents_full_name'],
                age=request.form['age'],
                address=request.form['address'],
                phone_number=request.form['phone_number'],
                courses=request.form['courses'],
                teacher_id=request.form['teacher_id']


            )
            #add to database and commit
            db.session.add(new_student)
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
        return redirect(url_for('index'))
    
    students = Student.query.all()
    return render_template('index.html', students=students)


@app.route('/delete/<int:id>', methods = ["POST"])
def delete(id):
    student = Student.query.get_or_404(id)
    try:
        db.session.delete(student)
        db.session.commit()
        return redirect('/')
    except Exception as e:
        db.session.rollback()
    return redirect(url_for('index'))
    

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        student.first_name = request.form['first_name']
        student.last_name = request.form['last_name']
        student.student_id = request.form.get('student_id', '')
        student.email = request.form['email']
        student.parents_full_name = request.form['parents_full_name']
        student.age = request.form['age']
        student.address = request.form['address']
        student.phone_number = request.form['phone_number']
        student.courses = request.form['courses']
        student.teacher_id = request.form['teacher_id']


        try:
            db.session.commit()
            return redirect('/')
        except Exception as e:
            db.session.rollback()
    return render_template('update.html', student=student)

@app.route('/teacher_view')
def teacher_view():
    students = Student.query.all()
    
    teacher_students = []
    for student in students:
        teacher_students.append({
            'id': student.id,
            'name': f"{student.first_name} {student.last_name}",
            'level': student.courses,  
            'day': "Mon",  # Placeholder (add w needs to be added)
            'time': "4:30 PM",  # Placeholder
            'email': student.email,
            'phone': student.phone_number
        })
    
    return render_template('teacher_view.html', students=teacher_students)

@app.route('/teachers')
def teachers_table():
    students = Student.query.all()  # get all students from DB
    return render_template('teachers.html', students=students)

@app.route('/')
def student_registration():
    students = Student.query.all()  # get all students
    return render_template('index.html', students=students)

@app.route('/teachers')
def teachers_table():
    students = Student.query.all()  # get all students
    return render_template('indexT.html', students=students)

#get all students
@app.route('/api/students', methods=['GET'])
def api_get_students():
    students = Student.query.order_by(Student.date_registered).all()#student reg doesnt do anything
    return jsonify([student.to_dict() for student in students])

#create new students
@app.route('/api/students', methods=['POST'])
def api_add_student():
    data = request.get_json()
    try:
        new_student = Student(
            first_name=data['first_name'],
            last_name=data['last_name'],
            student_id=data.get('student_id', ''),
            email=data['email'],
            parents_full_name=data['parents_full_name'],
            age=data['age'],
            address=data['address'],
            phone_number=data['phone_number'],
            courses=data['courses'],
            teacher_id=data['teacher_id']

        )
        db.session.add(new_student)
        db.session.commit()
        return jsonify(new_student.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error':str(e)}), 400

#get one stuednt
@app.route('/api/students/<int:id>', methods = ['GET'])
def api_get_student(id):
    student = Student.query.get_or_404(id)
    return jsonify(student.to_dict())

#updates students info
@app.route('/api/students/<int:id>', methods=['PUT'])
def api_update_student(id):
    student = Student.query.get_or_404(id)
    data = request.get_json()
    try:
        student.first_name = data['first_name']
        student.last_name = data['last_name']
        student.student_id = data.get('student_id', '')
        student.email = data['email']
        student.parents_full_name=data['parents_full_name']
        student.age=data['age']
        student.address=data['address']
        student.phone_number=data['phone_number']
        student.courses=data['courses']
        student.teacher_id=data['teacher_id']

        db.session.commit()
        return jsonify(student.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@app.route('/api/students/<int:id>', methods=['DELETE'])
def api_delete_student(id):
    student = Student.query.get_or_404(id)
    try:
        db.session.delete(student)
        db.session.commit()
        return jsonify({'message': 'Student deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)