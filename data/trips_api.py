import flask
from flask import jsonify, request

from . import db_session
from .plans import Plan

blueprint = flask.Blueprint(
    'trips_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/trips')
def get_users():
    db_sess = db_session.create_session()
    plans = db_sess.query(Plan).all()
    return jsonify(
        {
            'trips':
                [item.to_dict(only=(
                    'place', 'count_people', 'data', 'time', 'leader_id')) for item
                    in plans]
        }
    )

@blueprint.route('/api/trips', methods=['POST'])
def create_trips():
    db_sess = db_session.create_session()
    trips = Plan(
        place=request.json['place'],
        count_people=request.json['count_people'],
        data=request.json['data'],
        time=request.json['time'],
        leader_id=request.json['leader_id']
    )
    db_sess.add(trips)
    db_sess.commit()
    return jsonify({'id': trips.id})