from flask import Flask
from flask import Blueprint

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    @app.route("/hello")
    def hello():
        return "Hello, World!"
    
    from . import routes
    app.register_blueprint(routes.bp)

    return app