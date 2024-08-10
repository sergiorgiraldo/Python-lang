from storm.locals import *
from flask import g

testing = False

def init_app(app):
    connect_to_database()

    app.teardown_appcontext(close_db)

def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()
        
def connect_to_database():
    if testing:
        db = create_database("sqlite:")
        store = Store(db)
        # note: this is being executed only through the unit tests and the unit tests
        # position itself in the root folder (see the sys.path in the top of the file)
        # that's why I use the path as ./
        with open('./ddl/tbl-user-review-cycle.sql', 'r') as f:
            store.execute(f.read() + ';')
        with open('./ddl/tbl-user-list.sql', 'r') as f:
            store.execute(f.read() + ';')
        with open('./ddl/tbl-user-review.sql', 'r') as f:
            store.execute(f.read() + ';')
        with open('./ddl/insert-users.sql', 'r') as f:
            for line in f:
                store.execute(line)
        store.commit()
    else:
        db = create_database("postgres://GK47LX@localhost:5432/postgres")
        store = Store(db)

    g.db = db
    g.store = store