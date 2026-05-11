import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Plan(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'plans'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    place = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    count_people = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    users_count_now = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    data = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    time = sqlalchemy.Column(sqlalchemy.Time, nullable=True)
    leader_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))

    leader = orm.relationship('User', back_populates='plans')