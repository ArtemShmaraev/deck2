from flask import jsonify
from data import db_session, api
from data.users import User
from flask_restful import reqparse, abort, Resource
from random import randint


parser = reqparse.RequestParser()
parser.add_argument('surname', required=True)
parser.add_argument('name', required=True)
parser.add_argument('address', required=True)
parser.add_argument('email', required=True)
parser.add_argument('pass', required=True)
parser.add_argument('tel', required=True)


def abort_if_news_not_found(id):
    session = db_session.create_session()
    news = session.query(User).get(id)
    if not news:
        abort(404, message=f"Users {id} not found")


class UsersResource(Resource):
    def get(self, id):
        abort_if_news_not_found(id)
        session = db_session.create_session()
        users = session.query(User).get(id)
        return jsonify({'user': users.to_dict(
            only=('id', 'surname', 'name', 'address', 'email', 'tel'))})

    def delete(self, id):
        abort_if_news_not_found(id)
        session = db_session.create_session()
        news = session.query(User).get(id)
        session.delete(news)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('id', 'surname', 'name', 'address', 'email', 'tel')) for item in users]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        if session.query(User).filter(User.email == args['email']).first():
            return jsonify({'success': 'BAD EMAIL'})
        user = User(
            surname=args['surname'],
            name=args['name'],
            address=args['address'],
            tel=args['tel'],
            email=args['email'],
            code=str(randint(1000, 9999)),
            img='img/site/anon.png',
            is_good="0"
        )

        user.set_password(args['pass'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
