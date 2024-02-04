from flask import render_template, flash, redirect, url_for, request, g, \
    current_app, session
from flask_login import current_user, login_required
from flask_babel import _, get_locale
# from guess_language import guess_language
from app import db
from app.main.forms import EditProfileForm, RatingForm, LunchResturantForm
from app.main.models import User, Rating, LunchResturant
from app.main import bp
from calendar import Calendar
from datetime import datetime, date, timedelta
from sqlalchemy import func
from dateutil import relativedelta
from rocketchat_API.rocketchat import RocketChat
import calendar
from sqlalchemy import desc, asc
import os


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())
    g.user = current_user


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    sort_order  = request.args.get('so', 'desc')
    sort_column = request.args.get('sc', 'name')
    print(f"sort_order: {sort_order} sort_column: {sort_column}")

    page = request.args.get('page', 1, type=int)
    alllunchresturant = None
    if sort_order == "desc" and sort_column == "name":
        print("desc & name")
        alllunchresturant = LunchResturant.query.order_by(LunchResturant.name.desc()).paginate(
            page=page, per_page=current_app.config['POSTS_PER_PAGE'])
    elif sort_order == "asc" and sort_column == "name":
        print("asc & name")
        alllunchresturant = LunchResturant.query.order_by(LunchResturant.name.asc()).paginate(
            page=page, per_page=current_app.config['POSTS_PER_PAGE'])
    elif sort_order == "desc" and sort_column == "rating":
        print("desc & rating")
        alllunchresturant = LunchResturant.query.order_by(LunchResturant.average_rating.desc()).paginate(
            page=page, per_page=current_app.config['POSTS_PER_PAGE'])
    elif sort_order == "asc" and sort_column == "rating":
        print("asc & rating")
        alllunchresturant = LunchResturant.query.order_by(LunchResturant.average_rating.asc()).paginate(
            page=page, per_page=current_app.config['POSTS_PER_PAGE'])
    else:
        print("default rating desc")
        alllunchresturant = LunchResturant.query.order_by(LunchResturant.average_rating.desc()).paginate(
            page=page, per_page=current_app.config['POSTS_PER_PAGE'])

    next_url = url_for('main.lunchresturant_list', page=alllunchresturant.next_num) \
        if alllunchresturant.has_next else None
    prev_url = url_for('main.lunchresturant_list', page=alllunchresturant.prev_num) \
        if alllunchresturant.has_prev else None


    return render_template('lunchresturant.html', title=_('lunchresturant'),
                           alllunchresturant=alllunchresturant.items, next_url=next_url,
                           prev_url=prev_url, so=sort_order, sc=sort_column)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()

    page = request.args.get('page', 1, type=int)
    users_rating = Rating.query.filter(Rating.user_id == user.id).paginate(
            page = page, per_page = current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.user', username=user.username, page=users_rating.next_num) if users_rating.has_next else None
    prev_url = url_for('main.user', username=user.username, page=users_rating.prev_num) if users_rating.has_prev else None
    return render_template('user.html', user=user, allrating=users_rating.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/user/list')
@login_required
def user_list():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.username).paginate(
        page = page, per_page = current_app.config['POSTS_PER_PAGE'])

    next_url = url_for('main.user_list', page=users.next_num) if users.has_next else None
    prev_url = url_for('main.user_list', page=users.prev_num) if users.has_prev else None
    return render_template('users.html', users=users.items,
                           next_url=next_url, prev_url=prev_url)




@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)


@bp.route('/rating/add', methods=['GET', 'POST'])
@login_required
def rating_add():

    restid = request.args.get('restid')

    lunchresturant = LunchResturant.query.get(restid)

    if lunchresturant is None:
        return render_template('index.html', title=_('Supplied resturant not found'))

    form = RatingForm()
    if 'cancel' in request.form:
        return redirect(url_for('main.index'))

    user = User.query.filter_by(username=current_user.username).first_or_404()

    if user is None:
        return render_template('index.html', title=_('Logged in user not found'))

    # find existing rating from the current user
    existing_rating = Rating.query.filter(( Rating.resturant_id == form.lunchresturant.data)
                                          & ( Rating.user_id == user.id )).first()
    if existing_rating is not None:
        print(f'existing rating was found')
    else:
        print(f'NO existing rating was found, ')

    if request.method == 'POST' and form.validate_on_submit():

        rating = None
        if existing_rating is not None:
            rating = existing_rating
        else:
            rating = Rating(rating=form.rating.data)

        rating.resturant_id = form.lunchresturant.data
        rating.meal = form.meal.data
        rating.user_id = user.id
        rating.comment = form.comment.data

        db.session.add(rating)
        db.session.commit()

        rating.resturant.update_average_rating()
        db.session.commit()

        if existing_rating is not None:
            flash(_('Your rating is now updated!'))
        else:
            flash(_('New rating is now saved!'))

        new_rating_mess = 'new rating: %s\t%s\t%s' % (
                         rating.resturant.name, rating.meal, rating.comment)
        if current_app.config['ROCKET_ENABLED']:
            rocket = RocketChat(current_app.config['ROCKET_USER'],
                                current_app.config['ROCKET_PASS'],
                                server_url=current_app.config['ROCKET_URL'])
            rocket.chat_post_message(
             new_rating_mess,
             channel=current_app.config['ROCKET_CHANNEL']
             ).json()

        return redirect(url_for('main.index'))

    else:

        if existing_rating is not None:
            flash(_('Your existing rating will be updated!'))

        form.lunchresturant.choices = [(lunchresturant.id, lunchresturant.name)]

        # TODO figure out how to show rating added by the current user this session
        return render_template('rating.html', title=_('Add Rating'),
                               form=form)


@bp.route('/rating/edit/', methods=['GET', 'POST'])
@login_required
def rating_edit():

    ratingid = request.args.get('id')

    if 'cancel' in request.form:
        return redirect(url_for('main.index'))
    if 'delete' in request.form:
        return redirect(url_for('main.rating_delete', rating=ratingid))

    rating = Rating.query.get(ratingid)

    if rating is None:
        return render_template('rating.html', title=_('Rating is not defined'))

    form = RatingForm(obj=rating)

    if request.method == 'POST' and form.validate_on_submit():

        if current_app.config['ENFORCE_ROLES'] is True:
            user = User.query.filter_by(username=current_user.username).first()
            if user.role != "admin" and rating.user_id != user.id:
                flash(_('Users may only edit their own ratings'))
                return redirect(url_for('main.index'))

        rating.rating = form.rating.data
        rating.meal = form.meal.data
        rating.comment = form.comment.data
        db.session.commit()

        rating.resturant.update_average_rating()
        db.session.commit()

        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.index'))

    else:

        form.lunchresturant.choices = [(rating.resturant.id, rating.resturant.name)]
        form.rating.data  = rating.rating
        form.meal.data    = rating.meal
        form.comment.data = rating.comment

    return render_template('index.html', title=_('Edit Rating'),
                           form=form)


@bp.route('/rating/list/', methods=['GET', 'POST'])
@login_required
def rating_list():

    sort_order  = request.args.get('so', 'desc')
    sort_column = request.args.get('sc', 'name')
    print(f"sort_order: {sort_order} sort_column: {sort_column}")

    page = request.args.get('page', 1, type=int)

    if sort_order == "desc" and sort_column == "rating":
        rating = Rating.query.order_by(Rating.rating.desc()).paginate(
            page=page, per_page=current_app.config['POSTS_PER_PAGE'])

    elif sort_order == "asc" and sort_column == "rating":
        rating = Rating.query.order_by(Rating.rating.asc()).paginate(
            page=page, per_page=current_app.config['POSTS_PER_PAGE'])

    elif sort_order == "desc" and sort_column == "resturant":
        rating = db.session.query(Rating).join(LunchResturant).filter(Rating.resturant_id == LunchResturant.id).order_by(LunchResturant.name.desc()).paginate(page=page, per_page=current_app.config['POSTS_PER_PAGE'])

    elif sort_order == "asc" and sort_column == "resturant":
        rating = db.session.query(Rating).join(LunchResturant).filter(Rating.resturant_id == LunchResturant.id).order_by(LunchResturant.name.asc()).paginate(page=page, per_page=current_app.config['POSTS_PER_PAGE'])

    elif sort_order == "desc" and sort_column == "user":
        rating = db.session.query(Rating).join(User).filter(Rating.user_id == User.id).order_by(User.username.desc()).paginate(page=page, per_page=current_app.config['POSTS_PER_PAGE'])

    else:
        rating = db.session.query(Rating).join(User).filter(Rating.user_id == User.id).order_by(User.username.asc()).paginate(page=page, per_page=current_app.config['POSTS_PER_PAGE'])


    next_url = url_for('main.rating_list', page=rating.next_num) \
        if rating.has_next else None
    prev_url = url_for('main.rating_list', page=rating.prev_num) \
        if rating.has_prev else None

    return render_template('rating.html', title=_('Rating'),
                           allrating=rating.items, next_url=next_url,
                           prev_url=prev_url, so=sort_order,
                           sc=sort_column)


@bp.route('/rating/<id>', methods=['GET', 'POST'])
@login_required
def rating_view(id):

    rating = Rating.query.get(id)

    return render_template('rating.html', title=_('Rating'),
                           rating=rating)


@bp.route('/rating/delete/', methods=['GET', 'POST'])
@login_required
def rating_delete():

    ratingid = request.args.get('id')
    rating = Rating.query.get(ratingid)

    if rating is None:
        flash(_('Rating was not deleted, id not found!'))
        return redirect(url_for('main.index'))

    deleted_msg = 'Rating deleted: %s\t%s\t%s\t@%s\n' % (rating.resturant.name, rating.rating,
                                                           rating.comment, rating.user.username)

    form = RatingForm(obj=rating)

    if request.method == 'POST' and form.validate_on_submit():

        user = User.query.filter_by(username=current_user.username).first()
        if user.role != "admin" and form.user.data != user.id:
            flash(_('Users may only edit their own ratings'))
            return redirect(url_for('main.index'))

    flash(deleted_msg)
# error this till calculate wrong
    lunchresturant = LunchResturant.query.get(rating.resturant.id)

    db.session.delete(rating)
    db.session.commit()

    lunchresturant.update_average_rating()
    db.session.commit()
    return redirect(url_for('main.index'))


@bp.route('/lunchresturant/add', methods=['GET', 'POST'])
@login_required
def lunchresturant_add():

    if 'cancel' in request.form:
        return redirect(url_for('main.index'))

    form = LunchResturantForm()

    if request.method == 'POST' and form.validate_on_submit():

        if current_app.config['ENFORCE_ROLES'] is True:
            user = User.query.filter_by(username=current_user.username).first()

        lunchresturant = LunchResturant(name=form.name.data)
        db.session.add(lunchresturant)
        db.session.commit()
        flash(_('New lunchresturant is now posted!'))
        print("rocket enabled?: %s" % current_app.config['ROCKET_ENABLED'])
        if current_app.config['ROCKET_ENABLED']:
            rocket = RocketChat(current_app.config['ROCKET_USER'],
                                current_app.config['ROCKET_PASS'],
                                server_url=current_app.config['ROCKET_URL'])
            rocket.chat_post_message('new lunchresturant: %s\t%s\t%s\t@%s ' % (
                                 lunchresturant.start, lunchresturant.stop, lunchresturant.status,
                                 lunchresturant.user.username),
                                 channel=current_app.config['ROCKET_CHANNEL']
                                 ).json()

        return redirect(url_for('main.index'))

    return render_template('lunchresturant.html', title=_('Add lunchresturant'),
                           form=form)


@bp.route('/lunchresturant/edit/', methods=['GET', 'POST'])
@login_required
def lunchresturant_edit():

    lunchresturantid = request.args.get('id')
    lunchresturant = LunchResturant.query.get(lunchresturantid)

    if 'cancel' in request.form:
        return redirect(url_for('main.index'))

    if 'delete' in request.form:
        return redirect(url_for('main.lunchresturant_delete', lunchresturant=lunchresturantid))

    if lunchresturant is None:
        render_template('lunchresturant.html', title=_('lunchresturant is not defined'))

    form = LunchResturantForm(formdata=request.form, obj=lunchresturant)

    if request.method == 'POST' and form.validate_on_submit():

        rocket_msg_from = 'edit of lunchresturant from: %s' % (lunchresturant.name)

        lunchresturant.location = form.location.data
        lunchresturant.about = form.about.data

        db.session.commit()
        flash(_('Your changes have been saved.'))
        if current_app.config['ROCKET_ENABLED']:
            rocket = RocketChat(current_app.config['ROCKET_USER'],
                                current_app.config['ROCKET_PASS'],
                                server_url=current_app.config['ROCKET_URL'])
            rocket_msg_to = 'to: %s ' % (lunchresturant.name)
            rocket.chat_post_message("%s\n%s\n\nby: %s" % (rocket_msg_from,
                                                           rocket_msg_to,
                                                           current_user.username),
                                     channel=current_app.config['ROCKET_CHANNEL']
                                     ).json()

        return redirect(url_for('main.index'))

    else:

        return render_template('index.html', title=_('Edit lunchresturant'),
                               form=form)

@bp.route('/lunchresturant/<id>', methods=['GET', 'POST'])
@login_required
def lunchresturant_view(id):
    page = request.args.get('page', 1, type=int)

    lunchresturant = LunchResturant.query.get(id)
    ratings = Rating.query.filter_by(resturant_id=lunchresturant.id).paginate(
            page=page, per_page=current_app.config['POSTS_PER_PAGE'])

    google_maps_api_key=current_app.config['GOOGLE_MAPS_API_KEY']
    next_url = url_for('main.lunchresturant_view', page=ratings.next_num) \
        if ratings.has_next else None
    prev_url = url_for('main.lunchresturant_view', page=ratings.prev_num) \
        if ratings.has_prev else None

    return render_template('lunchresturant.html', title=_('lunchresturant'),
                           lunchresturant=lunchresturant,
                           ratings=ratings, google_maps_api_key=google_maps_api_key,
                           next_url=next_url,
                           prev_url=prev_url)



@bp.route('/lunchresturant/list/', methods=['GET', 'POST'])
@login_required
def lunchresturant_list():

    page = request.args.get('page', 1, type=int)

    lunchresturant = LunchResturant.query.order_by(LunchResturant.name).paginate(
            page=page, per_page=current_app.config['POSTS_PER_PAGE'])

    next_url = url_for('main.lunchresturant_list', page=lunchresturant.next_num) \
        if lunchresturant.has_next else None
    prev_url = url_for('main.lunchresturant_list', page=lunchresturant.prev_num) \
        if lunchresturant.has_prev else None

    return render_template('lunchresturant.html', title=_('lunchresturant'),
                           alllunchresturant=lunchresturant.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/lunchresturant/delete/', methods=['GET', 'POST'])
@login_required
def lunchresturant_delete():

    lunchresturantid = request.args.get('lunchresturant')
    lunchresturant = LunchResturant.query.get(lunchresturantid)

    if lunchresturant is None:
        flash(_('LunchResturant was not deleted, id not found!'))
        return redirect(url_for('main.index'))


    deleted_msg = 'LunchResturant deleted: %s' % (lunchresturant.name)
    if current_app.config['ROCKET_ENABLED']:
        rocket = RocketChat(current_app.config['ROCKET_USER'],
                            current_app.config['ROCKET_PASS'],
                            server_url=current_app.config['ROCKET_URL'])
        rocket.chat_post_message('lunchresturant deleted: \n%s\n by: %s' % (
                             deleted_msg, current_user.username),
                             channel=current_app.config['ROCKET_CHANNEL']
                             ).json()
    flash(deleted_msg)
    db.session.delete(lunchresturant)
    db.session.commit()

    return redirect(url_for('main.index'))
