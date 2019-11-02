from flask_login import current_user, login_required
from flask import render_template, flash, redirect, url_for, Flask, abort, request, current_app

from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm
from .. import db
from ..models import User, Role, Permission, Post
from ..decorators import admin_required, permission_required
from ..utils import make_post_pagination

current_user: User
current_app: Flask


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(form.body.data, current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    posts_pagination, posts = make_post_pagination(Post.query)
    return render_template('index.html', form=form, posts=posts, posts_pagination=posts_pagination)


@main.route('/user/<username>')
def user_page(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts_pagination, posts = make_post_pagination(user.posts)
    return render_template('user.html', user=user, posts=posts, posts_pagination=posts_pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('Your profile has been update.')
        return redirect(url_for('.user_page', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_profile_admin(user_id: int):
    user = User.query.get_or_404(user_id)
    form = EditProfileAdminForm(user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.name = form.name.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated')
        return redirect(url_for('.user_page', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.name.data = user.name
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:post_id>')
def post_page(post_id: int):
    post = Post.query.get_or_404(post_id)
    return render_template('posts.html', posts=[post])


@main.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit(post_id: int):
    post = Post.query.get_or_404(post_id)
    if current_user != post.author and not current_user.can(Permission.WRITE):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been update.')
        return redirect(url_for('.post_page', post_id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.get_user_by_name(username)
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))

    current_user.follow(user)
    flash(f'You are now following {username}')
    return redirect(url_for('.user_page', username=username))


@main.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.get_user_by_name(username)
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))

    current_user.unfollow(user)
    flash(f'You are not following {username} anymore')


@main.route('/followers/<username>')
def followers(username):
    user = User.get_user_by_name(username)
    if user is None:
        flash('Invalid User.')
        return redirect(url_for('.index'))

    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page,
        per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title='Followers off',
                           endpoint='.followers', pagination=pagination, follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.get_user_by_name(username)
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)
