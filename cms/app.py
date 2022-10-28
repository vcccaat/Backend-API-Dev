from db import db
from db import Course, Assignment, User
from flask import Flask, request
import json


app = Flask(__name__)
db_filename = "cms.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    # db.session.query(Course).delete()
    # db.session.query(Assignment).delete()
    # db.session.query(User).delete()
    db.session.commit()
    db.create_all()


@app.route("/")
@app.route("/api/courses/")
def get_courses():
    """
    Endpoint for getting a course
    """
    return success_response({"courses": [t.serialize() for t in Course.query.all()]})


@app.route("/api/courses/", methods=["POST"])
def create_course():
    """
    Endpoint for creating a new course
    """
    body = json.loads(request.data)
    if body.get("code") == None or body.get("name") == None:
        return failure_response("didn't provide code or name", 400)
    new_course = Course(code=body.get("code"), name=body.get("name"))
    db.session.add(new_course)
    db.session.commit()
    return success_response(new_course.serialize(), 201)


@app.route("/api/courses/<int:course_id>/")
def get_course(course_id):
    """
    Endpoint for getting a course by id
    """
    course = Course.query.filter_by(id=course_id).first()
    if not course:
        return failure_response("course not found")
    return success_response(course.serialize())



@app.route("/api/courses/<int:course_id>/", methods=["DELETE"])
def delete_course(course_id):
    """
    Endpoint for deleting a course by id
    """
    course = Course.query.filter_by(id=course_id).first()
    if not course:
        return failure_response("course not found")
    db.session.delete(course)
    db.session.commit()
    return success_response(course.serialize())


@app.route("/api/courses/<int:course_id>/assignment/", methods=["POST"])
def create_assignment(course_id):
    """
    Endpoint for creating a assignment for a course by id
    """
    course = Course.query.filter_by(id=course_id).first()
    if not course:
        return failure_response("course not found")
    body = json.loads(request.data)
    if body.get("title") == None or body.get("due_date") == None:
        return failure_response("didn't provide info", 400)
    new_assignment = Assignment(
        title=body.get("title"),
        due_date=body.get("due_date"),
        course_id=course_id,
        course=course.simple_serialize()
    )
    db.session.add(new_assignment)
    db.session.commit()
    return success_response(new_assignment.serialize(),201)


@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Endpoint for creating a new user
    """
    body = json.loads(request.data)
    if body.get("netid") == None or body.get("name") == None:
        return failure_response("didn't provide netid or name", 400)
    new_user = User(name=body.get("name"), netid=body.get("netid"))
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.serialize(), 201)


@app.route("/api/users/<int:user_id>/")
def get_user(user_id):
    """
    Endpoint for getting a user by id
    """
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return failure_response("user not found")
    return success_response(user.serialize())


@app.route("/api/courses/<int:course_id>/add/", methods=["POST"])
def assign_user_to_course(course_id):
    """
    Endpoint for assigning a user to a course by id
    """  
    course = Course.query.filter_by(id=course_id).first()
    if not course:
        return failure_response("course not found") 
    body = json.loads(request.data)
    user_id = body.get("user_id")
    type = body.get("type")

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return failure_response("cannot find this user", 400)

    # if type == "instructors":
    #     course.instructors.append(user)
    # if type == "students":
    #     course.students.append(user)
    course.users.append(user)

    db.session.commit()
    return success_response(course.serialize())



# generalized response formats
def success_response(data, code=200):
    return json.dumps(data), code

def failure_response(message, code=404):
    return json.dumps({"error": message}), code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
