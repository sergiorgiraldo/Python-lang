from flask import Flask

def create_app(is_testing=False):
    app = Flask(__name__, instance_relative_config=True)
    app.testing = is_testing
    @app.route("/hello")
    def hello():
        return "hello world, john doe"
    
    from . import routes
    app.register_blueprint(routes.bp)

    from . import db
    db.init_app(app)

    return app