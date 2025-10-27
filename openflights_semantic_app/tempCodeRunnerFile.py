from flask import Flask
from app.routes import bp
import os
#from app import create_app


def create_app():
    # 👇 Explicitly tell Flask where templates are
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'app', 'templates'))

    app.register_blueprint(bp)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)