from app.api import bp
from flask import jsonify, current_app
from app.main.models import User, LunchResturant
from flask import url_for
from app import db
from app.api.errors import bad_request
from flask import request
from app.api.auth import token_auth
from pprint import pprint
from rocketchat_API.rocketchat import RocketChat

@bp.route('/lunchresturant', methods=['POST'])
@token_auth.login_required
def create_lunchresturant():
    data = request.get_json() or {}
    if 'name' not in data:
        return bad_request('must include name')

    check_lunchresturant = LunchResturant.query.filter_by(name=data['name']).first()
    if check_lunchresturant is not None:
        return bad_request('LunchResturant already exist with id: %s' % check_lunchresturant.id)

    lunchresturant = LunchResturant()
    lunchresturant.from_dict(data, new_lunchresturant=True)

    db.session.add(lunchresturant)
    db.session.commit()
    response = jsonify(lunchresturant.to_dict())

    response.status_code = 201
    response.headers['Location'] = url_for('api.get_lunchresturant', id=lunchresturant.id)
    return response


@bp.route('/lunchresturantlist', methods=['GET'])
@token_auth.login_required
def get_lunchresturantlist():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = LunchResturant.to_collection_dict(LunchResturant.query, page, per_page, 'api.get_lunchresturantlist')
    return jsonify(data)


@bp.route('/lunchresturant/<int:id>', methods=['GET'])
@bp.route('/lunchresturant/<name>', methods=['GET'])
@token_auth.login_required
def get_lunchresturant(id=None, name=None):
    if id is not None:
        return jsonify(LunchResturant.query.get_or_404(id).to_dict())
    elif name is not None:
        return jsonify(LunchResturant.query.filter_by(name=name).first_or_404().to_dict())
    else:
        return bad_request('must include lunchresturant-name or -id')


@bp.route('/lunchresturant/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_lunchresturant(id):
    lunchresturant = LunchResturant.query.get_or_404(id)
    data = request.get_json() or {}
    lunchresturant.from_dict(data, new_lunchresturant=False)
    db.session.commit()
    return jsonify(lunchresturant.to_dict())


@bp.route('/lunchresturant/<lunchresturantname>/adduser/<username>', methods=['POST'])
@token_auth.login_required
def add_user_to_lunchresturant(lunchresturantname=None, username=None):

    if lunchresturantname is None:
        return bad_request('must include lunchresturantname in url')

    if username is None:
        return bad_request('must include username fields')

    print("lunchresturant: {} and user: {}".format(lunchresturantname, username))
    lunchresturant = LunchResturant.query.filter(LunchResturant.name == lunchresturantname).first_or_404()
    user = User.query.filter(User.username == username).first()

    if lunchresturant is None:

        retdata = {}
        retdata['message'] = "Can not find lunchresturant"
        response = jsonify(retdata)
        response.status_code = 403
        return response

    if user is None:
        retdata = {}
        retdata['message'] = "Can not find user"
        retdata['user'] = username
        response = jsonify(retdata)
        response.status_code = 403
        return response

    for u in lunchresturant.users:
        if user.username == u.username:
            return bad_request('User already member of the lunchresturant')

    lunchresturant.users.append(user)
    db.session.commit()
    response = jsonify(lunchresturant.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_lunchresturant', id=lunchresturant.id)
    return response


@bp.route('/lunchresturant/<int:id>/users', methods=['GET'])
@bp.route('/lunchresturant/<name>/users', methods=['GET'])
@token_auth.login_required
def user_list(id=None, name=None):

    if name is not None:
        lunchresturant = LunchResturant.query.filter(LunchResturant.name == name).first_or_404()
    elif id is not None:
        lunchresturant = LunchResturant.query.get(id)
    else:
        return bad_request('must include user-name or id in URL')

    if lunchresturant is None:
        return bad_request('Error retriving the lunchresturant')

    response = jsonify(lunchresturant.users_dict())
    response.status_code = 201
    return response


@bp.route('/lunchresturant/<int:id>/manager/<username>', methods=['GET'])
@bp.route('/lunchresturant/<lunchresturantname>/manager/<username>', methods=['GET'])
@token_auth.login_required
def manager_of_lunchresturant(lunchresturantname=None, id=None, username=None):

    if lunchresturantname is None:
        return bad_request('must include lunchresturantname in url')

    if username is None:
        return bad_request('must include username fields')

    print("lunchresturant: {} manager: {}".format(lunchresturantname, username))

    lunchresturant = LunchResturant.query.filter(LunchResturant.name == lunchresturantname).first_or_404()
    user = User.query.filter_by(username=username).first()

    if lunchresturant is None:

        retdata = {}
        retdata['message'] = "Can not find lunchresturant"
        response = jsonify(retdata)
        response.status_code = 403
        return response

    if user is None:
        retdata = {}
        retdata['message'] = "Can not find user"
        retdata['user'] = username
        response = jsonify(retdata)
        response.status_code = 403
        return response

    lunchresturant.manager = user
    db.session.commit()
    response = jsonify(lunchresturant.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_lunchresturant', id=lunchresturant.id)
    return response
