from flask import jsonify, request, current_app, url_for
from . import api
from ..models import User, Post


@api.route('/users/<int:user_id>')
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_json())


@api.route('/users/<int:user_id>/posts/')
def get_user_posts(user_id):
    user: User = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev_page = url_for('api.get_user_posts', user_id=user_id, page=page - 1) if pagination.has_prev else None
    next_page = url_for('api.get_user_posts', user_id=user_id, page=page + 1) if pagination.has_next else None
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev_page,
        'next': next_page,
        'count': pagination.total
    })


@api.route('/users/<int:user_id>/timeline/')
def get_user_followed_posts(user_id):
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    pagination = user.followed_posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev_page = url_for('api.get_user_followed_posts', user_id=user_id, page=page - 1) if pagination.has_prev else None
    next_page = url_for('api.get_user_followed_posts', user_id=user_id, page=page + 1) if pagination.has_next else None
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev_page,
        'next': next_page,
        'count': pagination.total
    })
