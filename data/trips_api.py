import flask
from flask import jsonify, request, make_response

from . import db_session
from .plans import Plan
import datetime

blueprint = flask.Blueprint(
    'trips_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/trips')
def get_trips():
    db_sess = db_session.create_session()
    plans = db_sess.query(Plan).all()
    return jsonify(
        {
            'trips':
                [item.to_dict(only=(
                    'id', 'place', 'count_people', 'data', 'time', 'leader_id')) for item
                    in plans]
        }
    )

@blueprint.route('/api/trips', methods=['POST'])
def create_trips():
    db_sess = db_session.create_session()
    data = datetime.datetime.strptime(request.json['data'], "%d-%m-%Y")
    time = datetime.datetime.strptime(request.json['time'], "%H-%M").time()
    trips = Plan(
        place=request.json['place'],
        count_people=request.json['count_people'],
        data=data,
        time=time,
        leader_id=request.json['leader_id']
    )
    db_sess.add(trips)
    db_sess.commit()
    return jsonify({'id': trips.id})

@blueprint.route('/api/trips/<int:trips_id>', methods=['DELETE'])
def delete_trips(trips_id):
    db_sess = db_session.create_session()
    plans = db_sess.get(Plan, trips_id)
    if not plans:
        return make_response(jsonify({'error': 'Not found'}), 404)
    db_sess.delete(plans)
    db_sess.commit()
    return jsonify({'success': 'OK'})