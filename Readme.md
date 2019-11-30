# Flask Blog


## Set Flask App
`FLASK_APP=manage.py`

## Environment variables

Name | Value
--- | ---
MAIL_USERNAME | darkblog.flask@gmail.com
MAIL_PASSWORD | password
FLASK_APP | manage.py

## Flask console config
```import sys; print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend([WORKING_DIR_AND_PYTHON_PATHS])

from manage import app, Role, User, db, Post
ctx = app.test_request_context()
ctx.push()
```


## FLASK DB command

1) Init database: `flask db init`.

2) Upgrade db: `flask db upgrade`.

3) Migrate db: `flask db migrate`.

## DataBase Methods for console

1) Insert roles to database: ***Role.insert_roles()***.
2) Generate fake users: ***User.generate_fake(100)***.
3) Generate fake posts: ***Post.generate_fake(100)***.

## Run Server

`flask run`