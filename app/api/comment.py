from flask import jsonify, request, g, url_for, current_app

from . import api
from .decorators import permission_required
from app import db
from app.models import Post, Permission, Comment


@api.route('/comments/')
def get_comments():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    prev_page = url_for('api.get_comments', page=page - 1) if pagination.has_prev else None
    next_page = url_for('api.get_comments', page=page + 1) if pagination.has_next else None
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'prev': prev_page,
        'next': next_page,
        'count': pagination.total
    })


@api.route('/comments/<int:comment_id>')
def get_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    return jsonify(comment.to_json())


@api.route('/posts/<post_id>/comments/')
def get_post_comments(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    prev_page = url_for('api.get_post_comments', id=post_id, page=page - 1) if pagination.has_prev else None
    next_page = url_for('api.get_post_comments', id=post_id, page=page + 1) if pagination.has_next else None
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'prev': prev_page,
        'next': next_page,
        'count': pagination.total
    })


@api.route('/posts/<post_id>/comments/', methods=['POST'])
@permission_required(Permission.COMMENT)
def new_post_comment(post_id):
    post = Post.query.get_or_404(post_id)
    comment = Comment.from_json(request.json)
    comment.author = g.current_user
    comment.post = post
    db.session.add(comment)
    db.session.commit()
    return (
        jsonify(comment.to_json()),
        201,
        {'Location': url_for('api.get_comment', id=comment.id)}
    )
