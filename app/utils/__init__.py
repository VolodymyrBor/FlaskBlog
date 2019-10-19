from typing import Any, Tuple

from flask import current_app, Flask, request
from flask_sqlalchemy import Pagination

current_app: Flask


from ..models import Post


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

