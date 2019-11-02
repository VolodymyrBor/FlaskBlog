from typing import Any, Tuple

from flask import current_app, Flask, request
from flask_sqlalchemy import Pagination


from app.models import Post, Comment

current_app: Flask


def make_post_pagination(pageable) -> Tuple[Pagination, Any]:
    """ Make pagination for Post
    :param pageable: Object, that have method order_by from sqlalchemy
    :return: pagination, pagination's items: posts
    """
    page = request.args.get('page', 1, type=int)
    posts_pagination: Pagination = pageable.order_by(Post.timestamp.desc()).paginate(
        page,
        per_page=current_app.config['FLASK_POSTS_PER_PAGE'],
        error_out=False)
    posts = posts_pagination.items
    return posts_pagination, posts


def make_comments_pagination(post: Post) -> Tuple[Pagination, Any]:
    """ Make pagination for Comment
    :return: pagination, pagination's items: comments
    """
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / (current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1)
    comments_pagination: Pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page,
        per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = comments_pagination.items
    return comments_pagination, comments



