from app.api import bp
from flask import jsonify, current_app
from app.main.models import User, Rating
from flask import url_for
from app import db
from app.api.errors import bad_request
from flask import request
from app.api.auth import token_auth
from pprint import pprint
from rocketchat_API.rocketchat import RocketChat

# TODO: check role = admin ...
@bp.route('/rating', methods=['POST'])
@token_auth.login_required
def create_rating():
    data = request.get_json() or {}
    if 'name' not in data or 'color' not in data:
        return bad_request('must include name and color fields')

    check_rating = Rating.query.filter_by(name=data['name']).first()
    if check_rating is not None:
        return bad_request('Rating already exist with id: %s' % check_rating.id)

    rating = Rating()
    rating.from_dict(data, new_rating=True)

    db.session.add(rating)
    db.session.commit()
    response = jsonify(rating.to_dict())

    response.status_code = 201
    response.headers['Location'] = url_for('api.get_rating', id=rating.id)
    return response


@bp.route('/ratinglist', methods=['GET'])
@token_auth.login_required
def get_ratinglist():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Rating.to_collection_dict(Rating.query, page, per_page, 'api.get_ratinglist')
    return jsonify(data)


@bp.route('/rating/<int:id>', methods=['GET'])
@bp.route('/rating/<name>', methods=['GET'])
@token_auth.login_required
def get_rating(id=None, name=None):
    if id is not None:
        return jsonify(Rating.query.get_or_404(id).to_dict())
    elif name is not None:
        return jsonify(Rating.query.filter_by(name=name).first_or_404().to_dict())
    else:
        return bad_request('must include rating-name or -id')


@bp.route('/rating/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_rating(id):
    rating = Rating.query.get_or_404(id)
    data = request.get_json() or {}
    rating.from_dict(data, new_rating=False)
    db.session.commit()
    return jsonify(rating.to_dict())


@bp.route('/rating/<ratingname>/adduser/<username>', methods=['POST'])
@token_auth.login_required
def add_user_to_rating(ratingname=None, username=None):

    if ratingname is None:
        return bad_request('must include ratingname in url')

    if username is None:
        return bad_request('must include username fields')

    print("rating: {} and user: {}".format(ratingname, username))
    rating = Rating.query.filter(Rating.name == ratingname).first_or_404()
    user = User.query.filter(User.username == username).first()

    if rating is None:

        retdata = {}
        retdata['message'] = "Can not find rating"
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

    for u in rating.users:
        if user.username == u.username:
            return bad_request('User already member of the rating')

    rating.users.append(user)
    db.session.commit()
    response = jsonify(rating.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_rating', id=rating.id)
    return response


@bp.route('/rating/<int:id>/users', methods=['GET'])
@bp.route('/rating/<name>/users', methods=['GET'])
@token_auth.login_required
def user_list(id=None, name=None):

    if name is not None:
        rating = Rating.query.filter(Rating.name == name).first_or_404()
    elif id is not None:
        rating = Rating.query.get(id)
    else:
        return bad_request('must include user-name or id in URL')

    if rating is None:
        return bad_request('Error retriving the rating')

    response = jsonify(rating.users_dict())
    response.status_code = 201
    return response


@bp.route('/rating/<int:id>/manager/<username>', methods=['GET'])
@bp.route('/rating/<ratingname>/manager/<username>', methods=['GET'])
@token_auth.login_required
def manager_of_rating(ratingname=None, id=None, username=None):

    if ratingname is None:
        return bad_request('must include ratingname in url')

    if username is None:
        return bad_request('must include username fields')

    print("rating: {} manager: {}".format(ratingname, username))

    rating = Rating.query.filter(Rating.name == ratingname).first_or_404()
    user = User.query.filter_by(username=username).first()

    if rating is None:

        retdata = {}
        retdata['message'] = "Can not find rating"
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

    rating.manager = user
    db.session.commit()
    response = jsonify(rating.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_rating', id=rating.id)
    return response
