import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


# объекты типа товар
class Products(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'products'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    product = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    start_date = sqlalchemy.Column(sqlalchemy.String, default=datetime.date.today())
    is_finished = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    leader = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    img = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    opisanie = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user = orm.relation('User')

    def __repr__(self):
        return self.product
