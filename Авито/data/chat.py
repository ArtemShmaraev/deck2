import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase

# объект типа чат
class Chat(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'chat'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    first_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    second_id = sqlalchemy.Column(sqlalchemy.Integer)
    sms = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user = orm.relation('User')