#enter environment - .\env\Scripts\activate 
#INITIALIZE DATABASE ---> python -c "from app import 
# app, db; app.app_context().push(); db.create_all(); print('Database initialized')"
from flask import Flask, render_template, request, redirect
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' 
db = SQLAlchemy(app)

class Todo(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id
    
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'
    else:
        tasks = Todo.query.order_by(Todo.date_created).all() #28:31
        return render_template('index.html', tasks = tasks)
    

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'
    

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        student.first_name = request.form['first_name']
        student.last_name = request.form['last_name']
        student.student_id = request.form.get('student_id', '')
        student.email = request.form['email']
        try:
            db.session.commit()
            flash('Student updated successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating student: {str(e)}', 'danger')
    return render_template('update.html', student=student)

@app.route('/api/tasks', methods=['GET'])
def api_get_tasks():
    tasks = Todo.query.order_by(Todo.date_created).all()
    return jsonify([{'id': t.id, 'content': t.content} for t in tasks])

@app.route('/api/tasks', methods=['POST'])
def api_add_task():
    data = request.get_json()
    new_task = Todo(content=data['content'])
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'id': new_task.id}), 201

@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def api_delete_task(id):
    task = Todo.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted'}), 200

if __name__ == "__main__":
    app.run(debug=True)