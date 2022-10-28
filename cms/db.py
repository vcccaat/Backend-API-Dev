from unicodedata import category
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

# associate many-to-many relationship via join table
association_table = db.Table("association", db.Model.metadata,
    db.Column("course_id", db.Integer, db.ForeignKey("courses.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"))
)

# student_association_table = db.Table(
#   "student_association", db.Model.metadata,
#   db.Column("course_id", db.Integer, db.Foreignkey("courses.id")),
#   db.Column("user_id", db.Integer, db.Foreignkey("users.id")),
# )

# instructor_association_table = db.Table(
#   "instructor_association", db.Model.metadata,
#   db.Column("course_id", db.Integer, db.Foreignkey("courses.id")),
#   db.Column("user_id", db.Integer, db.Foreignkey("users.id")),
# )

class Course(db.Model): 
    """
    course model
    has a one-to-mandy relationship with the assignments model
    has a many-to-many relationship with the student model
    """   
    __tablename__ = "courses"    
    id = db.Column(db.Integer, primary_key=True)    
    code = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    assignments = db.relationship("Assignment", cascade="delete")
    users = db.relationship("User", secondary=association_table, back_populates="courses")
    
    # students = db.relationship("User", secondary=student_association_table, back_populates="courses")
    # instructors = db.relationship("User", secondary=instructor_association_table, back_populates="courses")
# TODO: differentiate instructors and students by two association_tables

    def __init__(self, **kwargs):
      """
      init course object
      """
      self.code = kwargs.get("code", "")
      self.name = kwargs.get("name", "")
      self.assignments = []
      self.users = []


    def serialize(self):  
      """
      convert object into json format
      """
      return {        
          "id": self.id,        
          "code": self.code,        
          "name": self.name,   
          "assignments": [s.simple_serialize() for s in self.assignments],
          "instructors":[s.simple_serialize() for s in self.users],
          "students":[s.simple_serialize() for s in self.users]
          }

    def simple_serialize(self):  
      """
      convert object into json format without assignment, student or instructor field
      """
      return {        
          "id": self.id,        
          "code": self.code,        
          "name": self.name,   
          }




class Assignment(db.Model):
    """
    Assignment model
    """
    __tablename__ = "assignments"    
    id = db.Column(db.Integer, primary_key=True)    
    title = db.Column(db.String, nullable=False)
    due_date = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)

    def __init__(self, **kwargs):
      """
      init assignment object
      """
      self.title = kwargs.get("title", "")
      self.due_date = kwargs.get("due_date", 0)
      self.course_id = kwargs.get("course_id")
      self.course = kwargs.get("course")
      

    def serialize(self):  
      """
      convert object into json format
      """
      return {        
          "id": self.id,        
          "title": self.title,        
          "due_date": self.due_date,    
          "course": self.course
      }

    def simple_serialize(self):  
      """
      convert object into json format without course field
      """
      return {        
          "id": self.id,        
          "title": self.title,        
          "due_date": self.due_date,    
      }



class User(db.Model):
  """
  user model
  """
  __tablename__ = "users"    
  id = db.Column(db.Integer, primary_key=True)    
  name = db.Column(db.String, nullable=False)
  netid = db.Column(db.String, nullable=False)
  courses = db.relationship("Course", secondary=association_table, back_populates="users")

  def __init__(self, **kwargs):
    """
    init user object
    """
    self.name = kwargs.get("name", "")
    self.netid = kwargs.get("netid", "")


  def serialize(self):  
    """
    convert object into json format
    """
    return {        
        "id": self.id,        
        "name": self.name,     
        "netid": self.netid,   
        "courses": [t.simple_serialize() for t in self.courses]
    }

  # to avoid infinite loop of serialize course and user
  def simple_serialize(self):  
    """
    convert object into json format without courses field
    """
    return {        
        "id": self.id,        
        "name": self.name,     
        "netid": self.netid
    }