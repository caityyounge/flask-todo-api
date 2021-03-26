from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db '
db = SQLAlchemy(app)


class ToDoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'Task = {self.task}, summary = {self.summary}'


# db.create_all()

task_post_args = reqparse.RequestParser()
task_post_args.add_argument('task', type=str, help='Task is required', required=True)
task_post_args.add_argument('summary', type=str, help='Summary is required', required=True)

task_update_args = reqparse.RequestParser()
task_update_args.add_argument('task', type=str, help='Task is required', required=True)
task_update_args.add_argument('summary', type=str, help='Summary is required', required=True)

resource_fields = {
    'id': fields.Integer,
    'task': fields.String,
    'summary': fields.String
}


class ToDoList(Resource):
    def get(self):
        todo_lst = ToDoModel.query.all()
        todos = []
        for item in todo_lst:
            todo_lst_data = {'task': item.task, 'summary': item.summary}
            todos.append(todo_lst_data)
        return {'tasks': todos}


class ToDo(Resource):
    @marshal_with(resource_fields)
    def get(self, todo_id):
        result = ToDoModel.query.filter_by(id=todo_id).first()
        return result

    @marshal_with(resource_fields)
    def post(self, todo_id):
        args = task_post_args.parse_args()
        result = ToDoModel.query.filter_by(id=todo_id).first()
        if result:
            abort(409, message='That ID has already been taken')
        else:
            new_todo = ToDoModel(id=todo_id, task=args['task'], summary=args['summary'])
            db.session.add(new_todo)
            db.session.commit()
            return new_todo, 201

    @marshal_with(resource_fields)
    def put(self, todo_id):
        args = task_post_args.parse_args()
        result = ToDoModel.query.filter_by(id=todo_id).first()
        if not result:
            abort(404, message='That ID does not exist.')
        if args['task']:
            result.task = args['task']
        if args['summary']:
            result.summary = args['summary']
        db.session.commit()
        return result, 201

    @marshal_with(resource_fields)
    def delete(self, todo_id):
        result = ToDoModel.query.filter_by(id=todo_id).first()
        if not result:
            abort(404, message='ID not found')
        if result:
            db.session.delete(result)
            db.session.commit()
            return '', 204


api.add_resource(ToDoList, '/todos')
api.add_resource(ToDo, '/todo/<int:todo_id>')

if __name__ == '__main__':
    app.run()
