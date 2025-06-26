from flask import Flask
from dotenv import load_dotenv
import os

from auth import auth_bp
from prompts import prompts_bp
from sessions import sessions_bp


load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "random-key")


app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(prompts_bp, url_prefix='/prompts')
app.register_blueprint(sessions_bp, url_prefix='/sessions')


if __name__ == '__main__':
    app.run(debug=True)
