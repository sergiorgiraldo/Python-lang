import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from flaskr import create_app

@pytest.fixture
def app():
    app = create_app(True)

    yield app

@pytest.fixture
def client(app):
    return app.test_client()