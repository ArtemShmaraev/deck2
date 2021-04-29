from flask import jsonify
from data import db_session, api
from data.product import Products
from flask_restful import reqparse, abort, Resource

parser = reqparse.RequestParser()
parser.add_argument('product', required=True)
parser.add_argument('price', required=True)
parser.add_argument('leader', required=True)
parser.add_argument('opisanie', required=True)


def abort_if_news_not_found(id):
    session = db_session.create_session()
    news = session.query(Products).get(id)
    if not news:
        abort(404, message=f"Prod {id} not found")


class ProdResource(Resource):
    def get(self, id):
        abort_if_news_not_found(id)
        session = db_session.create_session()
        users = session.query(Products).get(id)
        return jsonify({'user': users.to_dict(
            only=('id', 'product', 'price', 'is_finished', 'leader', 'opisanie'))})

    def delete(self, id):
        abort_if_news_not_found(id)
        session = db_session.create_session()
        news = session.query(Products).get(id)
        session.delete(news)
        session.commit()
        return jsonify({'success': 'OK'})


class ProdListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(Products).all()
        return jsonify({'users': [item.to_dict(
            only=('id', 'product', 'price', 'is_finished', 'leader', 'opisanie')) for item in users]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        product = Products(
            product=args['product'],
            leader=args['leader'],
            price=args['price'],
            img="img/site/anon.png",
            opisanie=args['opisanie'],
            is_finished=False
        )
        session.add(product)
        session.commit()
        return jsonify({'success': 'OK'})
