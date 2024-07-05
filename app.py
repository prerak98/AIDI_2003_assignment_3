from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import datetime
import os

app = Flask(__name__)
api = Api(app)

# base_dir = os.path.abspath(os.path.dirname(__file__))
# database_path = os.path.join(base_dir, 'student.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class StudentModel(db.Model):
	student_id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(200))
	last_name = db.Column(db.String(200))
	dob = db.Column(db.DateTime)
	amount_due = db.Column(db.Integer())
	created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
	updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.now)

# Ensure the database is created within the app context
with app.app_context():
    print("Creating the database...")
    db.create_all()
    print("Database created.")


class Student(Resource):
    def get(self):
        students = StudentModel.query.all()
        return jsonify([{
            'student_id': student.student_id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'dob': student.dob.strftime('%Y-%m-%d'),
            'amount_due': student.amount_due,
            'created_at': student.created_at,
            'updated_ad': student.updated_at
        } for student in students])

    def post(self):
        data = request.get_json()
        new_student = StudentModel(
            first_name=data['first_name'],
            last_name=data['last_name'],
            dob=datetime.datetime.strptime(data['dob'], '%Y-%m-%d'),
            amount_due=data['amount_due']
        )
        db.session.add(new_student)
        db.session.commit()
        return jsonify({
            'message': 'Student created successfully',
            'student': {
                'student_id': new_student.student_id,
                'first_name': new_student.first_name,
                'last_name': new_student.last_name,
                'dob': new_student.dob.strftime('%Y-%m-%d'),
                'amount_due': new_student.amount_due,
                'created_at': new_student.created_at,
                'updated_at': new_student.updated_at
            }
        })


class StudentDetail(Resource):
    # Get a single student by ID
    def get(self, student_id):
        student = StudentModel.query.filter_by(student_id=student_id).first()
        if not student:
            return jsonify({'message': 'Student not found'}), 404
        return jsonify({
            'student_id': student.student_id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'dob': student.dob.strftime('%Y-%m-%d'),
            'amount_due': student.amount_due,
            'created_at': student.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': student.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    # Update a student by ID
    def put(self, student_id):
        data = request.get_json()
        student = StudentModel.query.filter_by(student_id=student_id).first()
        if not student:
            return jsonify({'message': 'Student not found'}), 404
        # Check if 'dob' key exists in data
        if 'dob' in data:
            student.dob = datetime.datetime.strptime(data['dob'], '%Y-%m-%d')
        student.first_name = data.get('first_name', student.first_name)
        student.last_name = data.get('last_name', student.last_name)
        # student.dob = datetime.datetime.strptime(data['dob'], '%Y-%m-%d')
        student.amount_due = data.get('amount_due', student.amount_due)
        student.updated_at = datetime.datetime.utcnow()
        db.session.commit()
        return jsonify({
            'message': 'Student updated successfully',
            'student': {
                'student_id': student.student_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'dob': student.dob.strftime('%Y-%m-%d'),
                'amount_due': student.amount_due,
                'created_at': student.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': student.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })

    # Delete a student by ID
    def delete(self, student_id):
        student = StudentModel.query.filter_by(student_id=student_id).first()
        if not student:
            return jsonify({'message': 'Student not found'}), 404
        db.session.delete(student)
        db.session.commit()
        return jsonify({'message': 'Student deleted successfully'})


# Add the resource to the API
api.add_resource(Student, '/students')
api.add_resource(StudentDetail, '/students/<int:student_id>')


if __name__ == '__main__':
	app.run(debug=True)