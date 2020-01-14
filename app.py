from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_heroku import Heroku
import os

app = Flask(__name__)
CORS(app)
heroku = Heroku(app)

basedir = os.path.abspath(os.path.dirname(__file__))
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.sqlite")
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://pebfpkqksuascu:2e739bd9569a3902a9912c24b2a129d3be2f5e60e5f8a4091b0b31150a72526b@ec2-3-220-86-239.compute-1.amazonaws.com:5432/dc28rba1gm8tgk"

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Todo(db.Model):
  __tablename__ = "todos"
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100), nullable=False)
  done = db.Column(db.Boolean)

  def __init__(self, title, done):
    self.title = title
    self.done = done

class TodoSchema(ma.Schema):
  class Meta:
    fields = ("id", "title", "done")

todo_schema = TodoSchema()
todos_schema = TodoSchema(many=True)

# POST
@app.route("/todo", methods=["POST"])
def add_todo():
  title = request.json["title"]
  done = request.json["done"]

  new_todo = Todo(title, done)

  db.session.add(new_todo)
  db.session.commit()

  todo = Todo.query.get(new_todo.id)
  return todo_schema.jsonify(todo)


# GET
@app.route("/todos", methods=["GET"])
def get_todos():
  all_todos = Todo.query.all()
  result = todos_schema.dump(all_todos)

  return jsonify(result)


# PUT/PATCH by ID
@app.route("/todo/<id>", methods=["PATCH"])
def update_todo(id):
  todo = Todo.query.get(id)

  new_done = request.json["done"]

  todo.done = new_done

  db.session.commit()
  return todo_schema.jsonify(todo)

# DELETE
@app.route("/todo/<id>", methods=["DELETE"])
def delete_todo(id):
  todo = Todo.query.get(id)
  db.session.delete(todo)
  db.session.commit()

  return jsonify("Got rid of that ish!")


if __name__ == "__main__":
  app.debug = True
  app.run()