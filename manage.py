import os
from unittest import TestLoader, TextTestRunner

import click

from app import create_app, db
from app.models import User, Role, Post

app = create_app(os.getenv('FLASK_ENV') or 'default')


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Post=Post)


@app.cli.command()
@click.argument('test_names', nargs=-1)
def test(test_names):
    """Run the unit tests."""
    tests = TestLoader().loadTestsFromNames(test_names) if test_names else TestLoader().discover('tests')
    TextTestRunner(verbosity=2).run(tests)


